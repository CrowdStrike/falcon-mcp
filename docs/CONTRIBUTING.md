# Welcome

Welcome and thank you for your interest in contributing to a CrowdStrike project! We recognize contributing to a project is no small feat! The guidance here aspires to help onboard new community members into how CrowdStrike-led projects tend to operate, and by extension, make the contribution process easier.

## How do I make a contribution?

Never made an open source contribution before? Wondering how contributions work in CrowdStrike projects? Here is a quick rundown!

1. Find an issue that you are interested in addressing, or a feature you would like to add. These are often documented in the project repositories themselves, frequently in the `issues` section.

2. Fork the repository associated with project to your GitHub account. This means that you will have a copy of the repository under *your-GitHub-username/repository-name*.

   Guidance on how to fork a repository can be found at [https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#fork-an-example-repository](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#fork-an-example-repository).

3. Clone the repository to your local machine using ``git clone https://github.com/github-username/repository-name.git``.

    GitHub provides documentation on this process, including screenshots, here:
[https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository#about-cloning-a-repository](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository#about-cloning-a-repository)

4. Create a new branch for your changes. This ensures your modifications can be uniquely identified and can help prevent rebasing and history problems. A local development branch can be created by running a command similar to:

    ``git checkout -b BRANCH-NAME-HERE``

5. Make the appropriate changes for the issue you are trying to address or the feature you would like to add.

6. Run `isort` to make sure imports are sorted correctly. This helps maintain consistent code style across the project.

    ``isort .``

7. Add the file contents of the changed files to the "snapshot" git uses to manage the state of the project (also known as the index). Here is the git command that will add your changes:

    ``git add insert-paths-of-changed-files-here``

8. **Use conventional commits** to store the contents of the index with a descriptive, standardized message. This project uses [Conventional Commits](https://www.conventionalcommits.org/) to enable automated release workflows and maintain proper semantic versioning.

    **Conventional Commit Format:**

    ```text
    <type>[optional scope]: <description>

    [optional body]

    [optional footer(s)]
    ```

    **Common Types Used in This Project:**
    - `feat:` - A new feature (triggers minor version bump)
    - `fix:` - A bug fix (triggers patch version bump)
    - `docs:` - Documentation only changes
    - `refactor:` - Code changes that neither fix bugs nor add features
    - `test:` - Adding missing tests or correcting existing tests
    - `chore:` - Changes to build process, auxiliary tools, or maintenance

    **Examples with Good Scoping (Recommended):**

    ```bash
    # Module changes with specific scopes (preferred)
    git commit -m "feat(modules/cloud): add list kubernetes clusters tool"
    git commit -m "feat(modules/hosts): add list devices tool"
    git commit -m "fix(modules/detections): resolve authentication error"

    # Resource changes
    git commit -m "refactor(resources): reword FQL guide in cloud resource"
    git commit -m "feat(resources): add FQL guide for hosts module"

    # Documentation changes with scope
    git commit -m "docs(contributing): update conventional commits guidance"
    git commit -m "docs(modules): enhance module development guide"

    # Infrastructure changes
    git commit -m "feat(ci): add automated testing workflow"
    git commit -m "chore(docker): update container configurations"
    ```

    **How Scoped Commits Improve Changelogs:**

    The above commits would generate organized changelog entries like:

    ```markdown
    # Features
    - modules/cloud: add list kubernetes clusters tool
    - modules/hosts: add list devices tool
    - resources: add FQL guide for hosts module
    - ci: add automated testing workflow

    # Bug Fixes
    - modules/detections: resolve authentication error

    # Refactors
    - resources: reword FQL guide in cloud resource

    # Documentation
    - contributing: update conventional commits guidance
    - modules: enhance module development guide
    ```

    **Basic Examples (Less Preferred but Acceptable):**

    ```bash
    # General examples without specific scopes
    git commit -m "feat: add new functionality"
    git commit -m "fix: resolve issue in application"
    git commit -m "docs: update documentation"
    ```

    **Breaking Changes:**
    For breaking changes, add `!` after the type or include `BREAKING CHANGE:` in the footer:

    ```bash
    git commit -m "feat!: change API authentication method"
    # or
    git commit -m "feat: update authentication system

    BREAKING CHANGE: API key format has changed"
    ```

    **Why Conventional Commits?**
    - **Automated Releases**: Enables automatic semantic version bumps and changelog generation
    - **Clear History**: Makes it easy to understand what type of changes were made
    - **Consistent Format**: Standardizes commit messages across all contributors

    For more details, see the [Conventional Commits specification](https://www.conventionalcommits.org/).

9. Push your local changes back to your account on github.com:

    ``git push origin BRANCH-NAME-HERE``

10. Submit a pull request to the upstream project. Documentation on this process, including screen shots, can be found at [https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork)

11. Once submitted, a maintainer will review your pull request. They may ask for additional changes, or clarification, so keep an eye out for communication! GitHub automatically sends an email to your email address whenever someone comments on your pull request.

12. While not all pull requests may be merged, celebrate your contribution whether or not your pull request is merged! All changes move the project forward, and we thank you for helping the community!

### Rebase Early, Rebase Often

Projects tend to move at a fast pace, which means your fork may become behind upstream. Keeping your local fork in sync with upstream is called `rebasing`. This ensures your local copy is frequently refreshed with the latest changes from the community.

Frequenty rebasing is *strongly* encouraged. If your local copy falls to far behind, you may encounter merge conflicts when submitting pull request. If this happens, you will have to triage (often by hand!) the differences in your local repository versus the changes upstream.

- Documentation on how to sync/rebase your fork can be found at [https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork)

- For handling merge conflicts, refer to [https://opensource.com/article/20/4/git-merge-conflict](https://opensource.com/article/20/4/git-merge-conflict)

## Where can I go for help?

### Submitting a Ticket

General questions relating a project should be opened in that projects repository. Examples would be troubleshooting errors, submitting bug reports, or asking a general question/request for clarification.

If your question is of the broader CrowdStrike community, please [open a community discussion](https://github.com/CrowdStrike/community/discussions/new).

### Submitting a New Project Idea

 If you do not see a project, repository, or would like the community to consider working on a specific piece of technology, please [open a community ticket](https://github.com/CrowdStrike/community/issues/new).

## What does the Code of Conduct mean for me?

Our community Code of Conduct helps us establish community norms and how they'll be enforced. Community members are expected to treat each other with respect and courtesy regardless of their identity.

CrowdStrike open source project maintainers are responsible for enforcing the CrowdStrike Code of Conduct within the project, issues may be raised directly to the maintainer should the need arise.

### Escalation Path

If you do not feel your concern has been addressed, if you are unable to communicate your concern with project maintainers, or if you feel the situation warrants, please escalate to:

- [oss-conduct@crowdstrike.com](mailto:oss-conduct@crowdstrike.com)
- [Ethics and Compliance Hotline](https://crowdstrike.ethicspoint.com/)
