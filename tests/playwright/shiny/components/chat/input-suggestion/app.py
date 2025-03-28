from shiny.express import ui

suggestions1 = """
<p>Here is the <span id="first" class='suggestion'>1st input suggestion</span>.
And here is a <span id="second" class='suggestion' data-suggestion='The actual suggestion'>2nd suggestion</span>.
Finally, a <img id="third" data-suggestion='A 3rd, image-based, suggestion' src='shiny-hex.svg' height="50px" alt='Shiny logo'> image suggestion.</p>
"""

suggestion2 = """
<p>On the other hand, <span id="fourth" class="suggestion submit">this suggestion will auto-submit</span>.
And <span id="fifth" data-suggestion="another suggestion" data-suggestion-submit="true">this suggestion will also auto-submit</span>.</p>
"""

chat = ui.Chat("chat", messages=[suggestion2])

chat.ui(messages=[suggestions1])


@chat.on_user_submit
async def on_user_submit(message: str):
    await chat.append_message(f"You said: {message}")
