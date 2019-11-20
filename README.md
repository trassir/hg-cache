## What?

This extension caches remote repository in directory specified by environment variable `HG_CACHE` to speed up `clone` and `pull` operations.

## Why?

Using mercurial (or any other VCS for that matter) in CI environments means retrieving same repository every time a certain job is executed. If working directory is cleaned before job executions, this usually causes repository to be `clone`-d from scratch causing unnecessary network traffic and increased job executiuon times. In same way, rarely executed job can be slowed down by `pull` operation when large bulk of changes needs to be downloaded.

## How?

`hg-cache` extention solves this problem by wrapping `clone` and `pull` operations with additional checks against locally-stored directory specified in `HG_CACHE` environment variable. As a result, most changes are copied (or even better - [hard-linked](https://www.mercurial-scm.org/wiki/RelinkExtension)) from local storage instead of downloading them from network.