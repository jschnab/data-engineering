# Git basics

## Overview

In this document, we describe how to install and setup git on your computer,
and how to work with a simple git workflow. It is a mix of my personal
experience and the [excellent
tutorial](https://medium.com/@zach.gollwitzer/git-crash-course-a-simple-workflow-for-small-teams-and-startups-c491919c9f77) by Zach Gollwitzer. I'll focus on Mac and Linux, please refer to the linked tutorial for Windows.

A great deal of resources for learning git is also accessible from
[Github](https://try.github.io).

## Install and setup git

On Mac, run:

```
brew install git
```

On Debian-like systems, run:

```
sudo apt install git
```

Configure your user settings by running:

```
git config --global user.name "First Last"
git config --global user.email "myemail@here.com"
```

To prevent potential mess with line endings, run:

```
git config --global core.autocrlf input
git config --global core.safecrlf true
```

Let's setup SSH authentication with Github. Check if you have an SSH key setup
on your computer by running:

```
ls -la ~/.ssh | grep 'id_rsa'
```

If it does not return the entries `id_rsa` and `id_rsa.pub`, you need to create an SSH
key by running:

```
cd ~ && ssh-keygen -t RSA
```

Once you have an SSH key, log in to Github and follow these steps:

1. click on your avatar on the top right corner
2. click on "Settings"
3. on the left menu, click on "SSH and GPG keys"
4. click on "New SSH key"
5. give the key a "Title" (e.g. "home-laptop")
6. paste the contents of your public SSH key (e.g. `~/.ssh/id_rsa.pub`) in the "Key" box
7. click on "Add SSH key"

From now on, you will be able to authenticate with Github via your SSH key. To
make sure this happens, when you *clone* a repository or setup a *remote* for you
repository, use `git@github.com/<username>/<repositoryname>.git`.

## Create a new repository

To create a new repository on Github, follow these steps:

1. click on your avatar on the top right corner
2. click on "Your repositories"
3. on the top right corner, click on "New" (green button)
4. give a name and a description to your repository
5. keep it public or make it private, depending on your goal
6. do not add a README.md or a license, we'll add these later
7. click on "Create repository"

## Initialize a git repository on your local computer

You should create a folder which will store the files belonging to your
repository. Go to this folder and run to initialize this folder as holding a
git repository:

```
git init
```

You need to add a *remote* Github repository to be able to *push* your files to
Github. To do so, follow these steps:

1. go to the relevant Github repository
2. click on "Code" (green button) on the right of the screen, and copy the
   repository ID corresponding to SSH (starting with `git@github.com...`)
3. go to your terminal and navigate to the folder of your repository
4. run `git remote add origin git@github...` (`origin` is the name of the
   remote)

You may want to exclude some files of your Github repository, for example large
CSV files resulting from your code. To instruct `git` to ignore certain files
or paths, you need to create a file named `.gitignore` in the root folder of
your repository, and add the paths you want to ignore to this file.

## Add a README file and make your first commit and push to the remote

You should write a good README.md file, especially if you expect people to read
your Github repository. This file should present the purpose of your
repository, and its contents.

If you don't know how to use the Markdown syntax, read [this
page](https://guides.github.com/features/mastering-markdown/).

Now is time to *stage* the files for your first commit. First you can check
your repository status by running:

```
git status
```

You should see a list of files colored red. These files are currently not
tracked by git.

Stage your files by running:

```
git add .
```

This will stage files in the current folder (`.`) and children of the current folder.
Now when you run `git status` you should see the staged filed colored green.

You can now *commit* your files and add a comment by running:

```
git commit -m "here's why I'm making this commit"
```

Now you can push your commit(s) to the *remote* by running:

```
git push origin master
```

where "origin" is the remote name and "master" is the branch name.

## Update the code in a git branch and make a merge request

When you contribute to a software project which uses version control, you
usually make code updates (new feature, bug fix, etc) in a *git branch* that is
different from the master branch. This allows to write the code without messing
with code that is deployed and running, which could potentially break it or
make a bug worse.

First you need to make sure your branch contains the most recent updates from
the remote repository (e.g. Github). Here we also assume there is not
uncommited code on your master branch, or on your current branch if different.
We also assume that your remote is named `origin`. To pull recent updates to the
master branch in Github, run:

```
git checkout master
git pull origin master
```

Now you can create a branch (named "myupdate" here) from the master branch:

```
git checkout -b myupdate
```

You are now in the branch "myupdate", so when you commit changes they will be
committed to this branch.

Make the necessary code updates and push your branch to Github:

```
git push -u origin myupdate
```

We use the argument `-u` to create an upstream branch as well as pushing our
commits to this branch.

We are now in good shape to make a "pull request" in Github language. You can
read the
[documentation](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)
for details but at a high level you should:

1. go to the page of your repository on Github
2. switch to the branch you want to merge using the branch menu
3. click on the "Pull request" button
4. verify that the target branch is relevant, e.g. master
5. type a title and description for the pull request
6. click on "Create Pull Request"
7. ask for a collaborator to review the pull request, and eventually approve it
   and merge it to the target branch

After your branch has been merge to the master branch, you should pull these
recent changes to your local master branch.

```
git checkout master
git pull origin master
```

You may also want to delete the merged branch:

```
git branch -d myupdate
```
