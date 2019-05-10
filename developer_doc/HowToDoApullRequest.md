One way to apply a pull request (there are others !!!)
=================

1. Make a fresh fork:
    * Go to the project to fork (for ex. populse/populse_mia).
    * Click on the top right button - Fork -.
    * Then make the fork (for ex. servoz/populse_mia).

2. Local cloning of this fork:
    * In your local station:
        * git lfs clone xxx # xxx can be found on the forked project in the GitHub site page (i.e. see the green button "Clone or download", for ex. xxx = https://github.com/servoz/populse_mia.git)

3. Some configurations:
    * In the local station and in the project (for ex. in  /home/toto/Git_Projects/populse_mia/):
        * git config remote.pushdefault origin # by default publish (i.e. with git push) in your fork, i.e. in https://github.com/servoz/populse_mia
        * git config push.default current # by default publish (i.e. with git push) on a branch with the same name as the current branch in the local repository
        * git remote add upstream xxx # Define upstream as the target project (that you have forked, i.e. xxx = https://github.com/populse/populse_mia)
        * git fetch upstream # gets the latest history from the project target on the server

4. Creation of an inProgress (inProgress is only an example!! You can choose the name you want as why not "MyFuckingPrettyBranch") branch (it is strongly recommended to work on your branch rather than on the master branch):
    * In the local station and in the project (for ex. in  /home/toto/Git_Projects/populse_mia/):
        * git checkout -b inProgress upstream/master # by adding upstream/master, branch inProgress is set up to track remote branch master from upstream

5. Make the modifications you need on your local fork (for ex. in /home/toto/Git_Projects/populse_mia/)
    * During your changes and at least at the end, check that all is added in the Index space by using:
        * git status # must not display the red message "Changes not staged for commit:"  but must display the green message "Changes to be committed :" (except if you don't want to apply a change in a file!). For this use "git add/rm/etc.. FileUwantToBeCommitted". If needed see man git, man git add, etc.)

6. Save your changes to your local repository (save from the Index space to the Header space):
    * git commit -m "AlittleTextSummarizingTheChange" # At this stage the command "git status" would return the message "nothing to commit, working tree clean"

7. Push your changes in your fork/branch in the remote server:
    * Git push # answer the login_name/passwd. Your changes are now in your remote server's fork (for ex. in  servoz/populse_mia and in your branch, for ex. in inProgress)

8. Finally, you must go through the project's web interface to create the pull-request from your fork (for ex. servoz/populse_mia) inProgress branch to the master branch of the reference repository (for ex. populse/populse_mia):
    * In the web page of your fork inProgress branch, click on the "New pull request" button. Write or complet the title and the comment fields. Then, finnaly, click the green button "Create pull request"

9. Actually, now, take in one hand the bible, in other a very big candle and wait for the deliberation of the reviewer ...
