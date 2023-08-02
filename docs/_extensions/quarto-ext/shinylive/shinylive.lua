local hasDoneShinyliveSetup = false
local codeblockScript = nil

-- Try calling `pandoc.pipe('shinylive', ...)` and if it fails, print a message
-- about installing shinylive package.
function callShinylive(args, input)
  local res
  local status, err = pcall(
    function()
      res = pandoc.pipe("shinylive", args, input)
    end
  )

  if not status then
    print(err)
    error("Error running 'shinylive' command. Perhaps you need to install the 'shinylive' Python package?")
  end

  return res
end


-- Do one-time setup when a Shinylive codeblock is encountered.
function ensureShinyliveSetup()
  if hasDoneShinyliveSetup then
    return
  end
  hasDoneShinyliveSetup = true

  -- Find the path to codeblock-to-json.ts and save it for later use.
  codeblockScript = callShinylive({ "codeblock-to-json-path" }, "")
  -- Remove trailing whitespace
  codeblockScript = codeblockScript:gsub("%s+$", "")

  local baseDeps = getShinyliveBaseDeps()
  for idx, dep in ipairs(baseDeps) do
    quarto.doc.add_html_dependency(dep)
  end

  quarto.doc.add_html_dependency(
    {
      name = "shinylive-quarto-css",
      stylesheets = {"resources/css/shinylive-quarto.css"}
    }
  )
end


function getShinyliveBaseDeps()
  -- Relative path from the current page to the root of the site. This is needed
  -- to find out where shinylive-sw.js is, relative to the current page.
  if quarto.project.offset == nil then
    error("The shinylive extension must be used in a Quarto project directory (with a _quarto.yml file).")
  end
  local depJson = callShinylive(
    { "base-deps", "--sw-dir", quarto.project.offset },
    ""
  )

  local deps = quarto.json.decode(depJson)
  return deps
end


return {
  {
    CodeBlock = function(el)
      if el.attr and el.attr.classes:includes("{shinylive-python}") then
        ensureShinyliveSetup()

        -- Convert code block to JSON string in the same format as app.json.
        local parsedCodeblockJson = pandoc.pipe(
          "quarto",
          { "run", codeblockScript },
          el.text
        )

        -- This contains "files" and "quartoArgs" keys.
        local parsedCodeblock = quarto.json.decode(parsedCodeblockJson)

        -- Find Python package dependencies for the current app.
        local appDepsJson = callShinylive(
          { "package-deps" },
          quarto.json.encode(parsedCodeblock["files"])
        )

        local appDeps = quarto.json.decode(appDepsJson)

        for idx, dep in ipairs(appDeps) do
          quarto.doc.attach_to_dependency("shinylive", dep)
        end

        el.attr.classes = pandoc.List()
        el.attr.classes:insert("shinylive-python")
        return el
      end
    end
  }
}
