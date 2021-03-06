[![codecov](https://codecov.io/gh/trassir/hg-cache/branch/master/graph/badge.svg)](https://codecov.io/gh/trassir/hg-cache)
[![Build Status](https://travis-ci.com/trassir/hg-cache.svg?branch=master)](https://travis-ci.com/trassir/hg-cache)
[![Build status](https://ci.appveyor.com/api/projects/status/w9qu5g2tic663wuj/branch/master?svg=true)](https://ci.appveyor.com/project/trassir/hg-cache/branch/master)

## What?

This extension caches remote repository in the directory specified by environment variable `HG_CACHE` to speed up `clone` and `pull` operations.

## Why?

Using mercurial (or any other VCS for that matter) in CI environments means retrieving same repository every time a certain job is executed. If the working directory is cleaned before job executions, this usually causes repository to be `clone`-d from scratch causing unnecessary network traffic and increased job execution times. In the same way, rarely executed job can be slowed down by `pull` operation when large bulk of changes needs to be downloaded.

## How?

`hg-cache` extention solves this problem by wrapping `clone` and `pull` operations with additional checks against locally-stored directory specified in `HG_CACHE` environment variable. As a result, most changes are copied (or even better - [hard-linked](https://www.mercurial-scm.org/wiki/RelinkExtension)) from local storage instead of downloading them from network.
