# Contributing to `bank2ynab`

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to `bank2ynab`. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document. This project is hosted by the organisation [bank2ynab](https://github.com/bank2ynab) which hereby expressly does not claim sole ownership and warmly welcomes all contributors.

-----
### Table Of Contents

[Code of Conduct](#code-of-conduct)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Style Guide](#style-guide)
  * [Coding Conventions](#coding-conventions)

[Additional Notes](#additional-notes)
  * [Using Labels](#using-labels)

----
## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project team listed there.

-----
## How Can I Contribute?

Please take a moment to review this document in order to make the contribution process easy and effective for everyone involved. Following these guidelines helps to communicate that you respect the time of the developers managing and developing this project. In return, they should reciprocate that respect in addressing your issue or assessing patches and features.

### Communication Channels

We primarily communicate via comments to issues. Sometimes we also use [Gitter](https://gitter.im/bank2ynab/Lobby) but Gitter doesn't notify users when there is new activity, so issues and comments are preferred.


### Reporting Bugs

This section guides you through submitting a bug report for `bank2ynab`. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](ISSUE_TEMPLATE.md), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one. Please do not re-open a closed issue because that confuses more than it helps.

#### Before Submitting A Bug Report

* **Check the [debugging guide](https://github.com/bank2ynab/bank2ynab/wiki/Debugging-Guide).** You might be able to find the cause of the problem and fix things yourself. Most importantly, check if you're using [the latest version of `bank2ynab`](https://github.com/bank2ynab/bank2ynab/archive/develop.zip) and if you can get the desired behavior by changing [`bank2ynab`'s config settings](https://github.com/bank2ynab/bank2ynab/wiki/userConfigs).
* **Check the [FAQs](https://github.com/bank2ynab/bank2ynab/wiki/FAQ)** for a list of common questions and problems.
* **Perform a [cursory search](https://github.com/bank2ynab/bank2ynab/issues)** to see if the problem has already been reported. If it has **and the issue is still open**, add a comment to the existing issue instead of opening a new one.

If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/bank2ynab/bank2ynab/issues/new).
* If possible, use the template to create the issue.
* **Use a clear and descriptive title** for the issue to identify the problem, and include a **clear description** with as much relevant information as possible. If you can, please include **test data** (anonymized) that causes the problem.
* [Assign labels](#using-labels) to the issue. Make a best guess if you're in doubt.

A good bug report shouldn't leave others needing to chase you up for more information. Please try to be as detailed as possible in your report. What is your environment? What steps will reproduce the issue? What OS and Python versions experience the problem? What would you expect to be the outcome? All these details will help people to fix any potential bugs.

#### **Do you have questions about the source code?**

* Ask any question about how to use `bank2ynab` by submitting a [new issue](https://github.com/bank2ynab/bank2ynab/issues/new).

#### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.
* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.
* Before submitting, please read the [Style Guide](#styleguide) to know more about our coding conventions.


### Suggesting Enhancements

Feature requests are welcome. But take a moment to find out whether your idea
fits with the scope and aims of the project. It's up to *you* to make a strong
case to convince the project's developers of the merits of this feature. Please
provide as much detail and context as possible.

This section guides you through submitting an enhancement suggestion for `bank2ynab`, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in the template, including the steps that you imagine you would take if the feature you're requesting existed.

#### Before Submitting An Enhancement Suggestion

* **Check the [debugging guide](https://github.com/bank2ynab/bank2ynab/wiki/Debugging-Guide)** for tips — you might discover that the enhancement is already available. Most importantly, check if you're using [the latest version of `bank2ynab`](https://github.com/bank2ynab/bank2ynab/archive/develop.zip) and if you can get the desired behavior by changing [`bank2ynab`'s config settings](https://github.com/bank2ynab/bank2ynab/wiki/userConfigs).
* **Perform a [cursory search](https://github.com/bank2ynab/bank2ynab/issues)** to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

If you're unable to find an open issue addressing your suggestion, [open a new one](https://github.com/bank2ynab/bank2ynab/issues/new).
* **Use a clear and descriptive title** for your suggestion, and include a **clear description** with as much relevant information as possible. If you can, please include **test data** (anonymized) that demonstrates the enhancement.


### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through these issues:

* [Beginner issues](https://github.com/bank2ynab/bank2ynab/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues](https://github.com/bank2ynab/bank2ynab/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) - issues which should be a bit more involved than `beginner` issues.

Note our wiki pages, especially the [Branching Strategy](https://github.com/bank2ynab/bank2ynab/wiki/BranchingStrategy)!

-----
## Style Guide


### Coding Conventions

Start reading our code and you'll get the hang of it.

* We optimize for readability.
* We indent using four spaces (soft tabs).
* We use [Travis](https://travis-ci.org/bank2ynab/bank2ynab/branches) for automated testing. Don't break it, keep Travis happy.
* This is open source software. Consider the people who will read your code, and make it look nice for them.
* (More to be added later?)


### Documentation Style Guide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Write clearly and concisely. Make it easy to understand, even for beginners.
* Whenever possible, include links to relevant issues, documents, wiki pages, and so on.

-----
## Additional Notes


### Using Labels

This section lists the labels we use to help us track and manage issues. Labels make it easy to find groups of issues. An issue can have one or several labels.

| Label name   | Description   |
| ------------ | ------------- |
| `bank format`                | This is a description of a bank's CSV export format. |
| `blocked`                    | This issue cannot progress until some other issue is complete. |
| `bug`                        | Confirmed bugs or reports that are very likely to be bugs. |
| `compatibility`              | E.g. a problem with Python 2.7 vs 3.5 |
| `documentation`              | Improvements to the documentation (issues, documents, wiki, release notes, etc.) |
| `duplicate`                  | This is a duplicate of one or more other issues, i.e. it has been reported before. |
| `enhancement`                | Feature requests. |
| `feedback`                   | General feedback more than bug reports or feature requests. |
| `good first issue`           | Less complex issues which would be good first issues to work on for new contributors. |
| `help wanted`                | The project (or assignee) would appreciate help from the community in resolving these issues. |
| `in progress`                | This is being worked on. |
| `invalid`                    | The described issue does not exist, or the issue should be disregarded for some other reason. |
| `meta`                       | Issues about how we handle this project rather than about specific functionality. |
| `more-information-needed`    | More information needs to be collected about these problems or feature requests (e.g. steps to reproduce). |
| `optimisation`               | This is an improvement to the program that does not change any functionality. |
| `pending new feature`        | (deprecated.) |
| `pending original developer` | We're waiting for a response from another developer. |
| `plugin needed`              | This issue requires a new plugin to be created. |
| `PRIORITY: AWAITING TRIAGE`  | Priority of the issue. |
| `PRIORITY: HIGH`             | Priority of the issue. |
| `PRIORITY: LOW`              | Priority of the issue. |
| `PRIORITY: MEDIUM`           | Priority of the issue. |
| `question`                   | Questions more than bug reports or feature requests (e.g. how do I do X). |
| `to be tested`               | This issue needs to be tested. |
| `wontfix`                    | The team has decided not to fix these issues for now, either because they're working as intended or for some other reason. |
| `workaround exists`          | The user can work around the problem for now, but a proper solution is needed. |

-----
`bank2ynab` is a volunteer effort. We encourage you to pitch in and join [the team](https://github.com/bank2ynab/bank2ynab/graphs/contributors)!

Thanks! :heart: :heart: :heart:

-----
This file is heavily inspired by other sources linked [here](https://help.github.com/articles/setting-guidelines-for-repository-contributors/#examples-of-contribution-guidelines).
