from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


class ChatModule:
    def __init__(self, page: Page, id: str, classes: str):
        self.id = id
        self.chat = controller.Chat(page, f"chat_{id}")
        self.classes = classes

    def expect_last_message_icon_to_have_classes(self):
        # TODO: Fix this test to find icon in shadow root
        last_msg_icon = self.chat.loc_latest_message.locator(
            '.message-icon > slot[name="icon"] > *'
        )
        expect(last_msg_icon).to_have_class(self.classes)


@skip_on_webkit
def test_validate_chat_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chats: list[ChatModule] = [
        ChatModule(page, "default", "bi bi-robot"),
        ChatModule(page, "otter", "fa icon-otter"),
        ChatModule(page, "svg", "bi bi-info-circle-fill icon-svg"),
        ChatModule(page, "shiny", "icon-shiny"),
    ]

    for mod in chats:
        expect(mod.chat.loc).to_be_visible(timeout=30 * 100)
        mod.expect_last_message_icon_to_have_classes()

        mod.chat.set_user_input(f"Hi {mod.id}.")
        mod.chat.send_user_input()

        mod.expect_last_message_icon_to_have_classes()
