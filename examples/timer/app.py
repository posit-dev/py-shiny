import datetime
import shiny as sh

ui = sh.page_fluid("The time is:", sh.output_text("time", inline=True))


def server(session: sh.ShinySession):
    @sh.reactive()
    def r():
        sh.invalidate_later(0)
        return datetime.datetime.now()

    @session.output("time")
    async def _():
        return str(r())


app = sh.ShinyApp(ui, server)

if __name__ == "__main__":
    app.run()
