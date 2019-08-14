# Apatite

A command-line application for curating structured lists of software projects.

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Apatite_taill%C3%A9e.jpg/320px-Apatite_taill%C3%A9e.jpg">

First run

`pip install apatite`

Then run

`apatite --help`

And you'll see

```
Usage: /home/mahmoud/virtualenvs/apatite/bin/apatite subcommand [FLAGS]

    automation and analytics for curated lists of awesome software.

    Normal analysis workflow:

      * apatite pull-repos  (can take 3-4 hours, 25GB on the full APA, use --targets to limit)
      * apatite collect-metrics
      * apatite export-metrics
      * apatite analyze  # TODO



Subcommands:

  render                    generate the list markdown from the yaml listing
  normalize                 normalize project and tag order, checking for duplicates and format divergences,
                            overwrites the yaml listing
  pull-repos                clone or pull all projects. requires git, hg, and bzr to be installed for projects in APA
  collect-metrics           use local clones of repositories (from pull-repos) to gather data about projects
  show-recent-metrics       shows the most recent metrics collection
  export-metrics            export a csv with metrics collated from previous collect-metrics runs
  show-exportable-metrics   show a list of metric names available for export-metrics --cols and --cols-file flags
  console                   use pdb to explore plist and pdir
  version                   print the apatite version and exit


Flags:

  --help / -h   show this help message and exit
```
