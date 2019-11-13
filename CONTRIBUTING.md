# How to Contribute

Hello there! Thank you for considering contributing to Awesome Python
Applications! Your help is essential to making APA the best project it
can be.

There are many ways to contribute, check out the
[TODO.md](https://github.com/mahmoud/awesome-python-applications/blob/master/TODO.md)
for examples, but a few of the common tasks are detailed below. These
descriptions might be inaccurate, so feel free to open an issue or a
work-in-progress Pull Request for clarification.

## Adding a project

First step, make sure the project isn't already on the list, or in our
"TODO", "archive", and "revisit" lists. We've reviewed thousands of
projects now, so chances aren't bad we've got it!

### The Easy Way

The easiest way to add a project is to submit an issue using the issue
template questionnaire. A maintainer will review and add the project
following the fun standard process below.

### The Fun Way

The APA is structured around a YAML file,
[projects.yaml](https://github.com/mahmoud/awesome-python-applications/blob/master/projects.yaml),
which is used to validate and generate the various lists, including
the RSS feed. A working install of
[apatite](https://github.com/mahmoud/apatite) (`pip install apatite`)
is required to render the documents before committing.

### Creating a Good Entry

At the time of writing the following is required to make a valid entry:

#### Project name

Try to use the preferred capitalization of the project. If two
separate projects share a name, feel free to use parentheses to
disambiguate.

#### Project description

Because this is the Awesome Python Application list, and all entries
must be free/open-source, there is no need to include the terms
"Python", "Application", "free", or "open-source" in the project
description.

Instead, focus on architecture (e.g., web application vs CLI), design,
features, and target userbase.

#### Links

Ultimately APA is about links and references, so we want as many as
possible. Some common forms:

* **`repo_url`** - Required link to code repository.  If it's not
  immediately obvious how to clone/download the code, a `clone_url`
  should also be supplied, provided the repo is `git`, `hg`, or `bzr`.
* `home_url` - Project landing page, if different than repo url
* `docs_url` - Documentation, user guide, or integration guide
* `fund_url` - A link to monetarily sponsor/support the project
* `demo_url` - For projects which are self-hostable, a site
  demonstrating the project in action, if different than `home_url`
* `wp_url` - A link to the Wikipedia article about the project (can be a section)
* `gh_url` - A link to a GitHub mirror if a non-GitHub-based project has one
* `pypi_url` - A link to the PyPI project page when the project has
  one. (most applications do not; PyPI is primarily for libraries)

Other keys of the form `*_url` will also be handled
automatically. There's rarely a reason to include the same URL under
multiple keys, so just pick the closest one.

#### Tags

Pick any appropriate entries from the `tagsonomy` at the top of
projects.yaml. At this point we require at least one "topic" tag, with
an option for secondary topic, and target platform.

Note that for target platform, "linux" typically means
desktop/single-user programs, whereas "server" is used for multi-user
applications.

Don't spend too long tagging projects with information which can be
automatically inferred, like license, dependencies, python version
compatibility, and others. The future direction here is to use `apatite` to
automatically fill those tags.


### Tips

1. The `projects.yaml` list is automatically sorted and
   normalized. Don't worry about finding the right spot to add a
   project. Add it at the top or at the bottom, with values in any
   order, and `apatite`'s rendering process will take care of the rest.
1. When adding a project with maintainers on github, try to use the
   commit message "adding project-xyz /cc @maintainer1 @maintainer2"
   so that the maintainers are somewhat aware of their presence on the
   list. This also helps in case we make a typo, include incorrect
   project information, or the project maintainers would prefer the
   project remain unlisted for now.


## Project criteria

There are few hard and fast rules, and all entries will be
respectfully reviewed on a case-by-base basis. That said, there are
some standards we'd like to uphold.

Target projects should be:

- [x] Free software with an online source repository.
- [x] Using Python for a considerable part of their functionality.
- [x] Well-known, or at least prominently used in an identifiable niche.
- [x] Maintained or otherwise demonstrably still functional on relevant platforms.
- [x] An application, not a library or framework.

Additional soft criteria that have proven useful in curating the list:

* A commit in the last year is usually enough for the maintenance
  requirement. At the time of writing over 95% of 360 projects have
  had a commit in the last year. (Note that this proportion is
  emergent, hence the soft rule)
* Projects smaller than 100 commits and fewer than 3 contributors are
  often too young and should be revisited.
* Categories, architectures, or domains which lack representation on
  the list should be given extra consideration. (Would love to see
  more Beeware, mobile, browser-based, and game projects)
* To maximize the audience, projects should be safe-for-work.
* Technologies and hype alone do not make an application
  awesome. Value provided to a userbase are far more important to the
  spirit of the list.
* Good candidates should generally not exist solely to demonstrate an
  underlying technology.

### What is an application?

While generally it's pretty easy to tell the difference between a
library and an application, that doesn't mean there aren't tricky
cases. Here are some helpful questions to help classify Python software:

* Does the software favor non-code configuration (environment
  variables, ini/yaml/toml/json files, CLI args, etc.) versus writing
  more Python code? Software may seem like an application at first,
  but if it requires writing too much code, it may actually be a
  framework.
* Does the software feature a plugin system? Extending the previous
  point, applications won't require writing code, but well-developed
  ones may feature a structured way to extend them.
* Is the software installed using the pip package manager? Being
  installed with (or requiring) system package managers and installers
  is generally a pretty good sign you're looking at an application.

## Overall goals

The APA isn't [the only list of Python software
around](https://github.com/mahmoud/awesome-python-applications/blob/master/TODO.md#other-lists). The
following represent the goals of this list versus many others:

1. More explicit criteria for inclusion
2. Guaranteed qualitative review (peer review, etc.)
3. Only applications, no frameworks or libraries
4. Links, specifically repo link required, for automated quality control (dead links, dead projects)
5. Human-readable docs, machine-readable structured data
6. Open-source: contribute via PR
7. Tagged, with mutliple tag dimensions (tagsonomy)
8. [Long-term vision](https://github.com/mahmoud/awesome-python-applications/blob/master/TODO.md#long-term-vision)

If you have ideas on how to achieve the above, we would love to hear
them. Please, [create an issue](https://github.com/mahmoud/awesome-python-applications/issues).
