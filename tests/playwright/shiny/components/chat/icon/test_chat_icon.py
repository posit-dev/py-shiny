from typing import Optional

from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


class ChatModule:
    def __init__(self, page: Page, id: str, classes: str):
        self.id = id
        self.chat = controller.Chat(page, f"chat_{id}")
        self.classes = classes

    def expect_last_message_icon_to_have_classes(self, classes: Optional[str] = None):
        last_msg_icon = self.chat.loc_latest_message.locator(".message-icon > *").first
        expect(last_msg_icon).to_have_class(classes or self.classes, timeout=30 * 1000)


@skip_on_webkit
def test_validate_chat_basic(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    chats: list[ChatModule] = [
        ChatModule(page, "default", "bi bi-robot"),
        ChatModule(page, "animal", "fa icon-otter"),
        ChatModule(page, "svg", "bi bi-info-circle-fill icon-svg"),
        ChatModule(page, "image", "icon-image grace-hopper"),
    ]

    for mod in chats:
        expect(mod.chat.loc).to_be_visible(timeout=30 * 1000)
        mod.expect_last_message_icon_to_have_classes()

        mod.chat.set_user_input(f"Hi {mod.id}.")
        mod.chat.send_user_input()

        mod.expect_last_message_icon_to_have_classes()

    # Test changing icons during the chat
    animal = controller.InputSelect(page, "animal")
    chat_animal = chats[1]

    animal.set("Hippo")
    chat_animal.chat.set_user_input("hello")
    chat_animal.chat.send_user_input()
    chat_animal.expect_last_message_icon_to_have_classes("fa icon-hippo")

    animal.set("Frog")
    chat_animal.chat.set_user_input("hello")
    chat_animal.chat.send_user_input()
    chat_animal.expect_last_message_icon_to_have_classes("fa icon-frog")

    # Test that the icon used is the default if no icon is sent
    # (the message-specific icon is just for that message)
    animal.set("Otter")
    chat_animal.chat.set_user_input("hello")
    chat_animal.chat.send_user_input()
    chat_animal.expect_last_message_icon_to_have_classes()

    # Test changing icon images during the chat
    image = controller.InputSelect(page, "image")
    chat_image = chats[3]

    image.set("Shiny")
    chat_image.chat.set_user_input("hi shiny")
    chat_image.chat.send_user_input()
    chat_image.expect_last_message_icon_to_have_classes("icon-image shiny")
