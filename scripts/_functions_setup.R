ensure_base_packages <- function() {
  for (pkg in c("cli", "pak")) {
    if (!requireNamespace(pkg, quietly = TRUE)) {
      message("Installing base package: ", pkg)
      install.packages(pkg, quiet = TRUE)
    }
  }
}

assert_npm_is_installed <- function() {
  if (Sys.which("npm")[["npm"]] == "") {
    cli::cli_abort(c(
      "{.strong {npm}} is required to install JavaScript dependenceis.",
      i = "Please install {.url https://nodejs.org}."
    ))
  }

  cli::cli_alert_success("{.strong npm} is installed")
  invisible(TRUE)
}

pak_install <- function(...) {
  ensure_base_packages()
  pkgs <- c(...)

  cli::cli_progress_step("Installing {length(pkgs)} package{?s}")

  capture.output(
    pak::pak(pkgs, upgrade = TRUE, ask = FALSE, lib = .libPaths()[1])
  )

  cli::cli_progress_done()

  cli::cli_h2("Packages")
  for (pkg in pkgs) {
    pkg_name <- pkg
    if (grepl("@", pkg)) {
      pkg_name <- basename(sub("@.+$", "", pkg))
    } else if (grepl("/", pkg)) {
      pkg_name <- basename(pkg)
    }
    v_pkg <- pkg_source_version(pkg_name)

    cli::cli_inform("Installed {.strong {pkg_name}} v{v_pkg}")
  }

  invisible(pkgs)
}

bs_version_full <- function(version) {
  bs_v <- bslib::versions()
  names(bs_v)[bs_v == version]
}

pkg_source_version <- function(pkg) {
  desc <- suppressWarnings(utils::packageDescription(pkg))
  if (!inherits(desc, "packageDescription")) {
    return("[not installed]")
  }
  version <- desc[["Version"]]
  if (is.null(desc[["GithubRepo"]])) {
    return(version)
  }

  sprintf(
    "%s (%s/%s@%s)",
    version,
    desc[["GithubUsername"]],
    desc[["GithubRepo"]],
    desc[["GithubSHA1"]]
  )
}
