# Auto-upload daily test results

## Python script to automatically upload your HW Daily Test Results to the Github test_results repo 

### Script description:
1. The script creates a git directory, if a directory already created, script updates it (step 2-3) (-g argument)
   * Fetches code from the source repo master branch zephyrproject-rtos/test_results
   * Pushes updates to the origin repo master branch, in my case it is maksimmasalski/test_results
2. Downloads versions.json file and finds the proper commit name using -c mandatory argument.
   * When version found, it remembers its name and deletes versions.json file (-c argument)
3. Creates a new branch using data from config.txt file, e.g. *companyname_daily_master_177f2dac8b*
4. Copies files from the Test results directory (-j argument) for a given commit to the .git repository *test_results*
5. The script does $git add for all test results files
6. The script does $git commit
7. The script does $git push 
   * New branch will be created in your origin repo
8. Checkouts back to the master branch. When you need to run the script again, all actions will be repeated again.
Script execution finished.
9. Now can open PR link from the terminal output or go to Github webpage and create the Pull Request to the upstream master branch. Github will generate a PR, you just click the "Compare & pull request" button on Github webpage.

### Sanitycheck command sample:
`sanitycheck --device-testing --hardware-map <map file> -p <platform> -T <tests path>`

### 1. Setup a common folder for target.xml files:
   * After you finished all sanitycheck runs for your platforms, put all `target.xml` files from `sanity-out` directories into a common folder. <br/>
   * That folder must have only `target.xml` files for the specified commit.<br/>
For example, I created folder `zephyr-v2.3.0-1307-gf014ba1ff1`, that folder stores only sanitycheck results `target.xml` files for that commit.<br/>
With that folder will work current script. It depends on your CI system how you will move `target.xml` files into a common folder. It can be performed with a bash script or manually.<br/>

### 2. Setup script and run:
1. Enter your credentials to access Github to the Git configuration file.
2. Setup config.txt file according to the comments in it
3. Export environment variable for GitPython log output:<br/>
`export GIT_PYTHON_TRACE=full`
4. Then run the script:<br/>
`python3 upload_to_github.py -c <commit> -j <path to the common folder with .xml files> -g <git dir path/test_results> -t <commit title> -m <commit message>`

**Example:**
1. `export GIT_PYTHON_TRACE=full`<br/>
2. `python3 upload_to_github.py -c zephyr-v2.3.0-1307-gf014ba1ff1 -j /home/ztest2/work/testreport/sumreport/master/zephyr-v2.3.0-1307-gf014ba1ff1 -g /home/maksim/test_results -t "Master Daily Test Report" -m "Zephyr Daily Test Report for the master branch"`

### Script has next mandatory arguments:
`-c` Upload daily test results of the given commit tag<br/>
`-j` Directory path to your daily test result files<br/>
`-g` Directory path to the git repo "test_results"<br/>
`-m` Commit message<br/>
`-t` Commit title<br/>

Script has built-in help command for the each argument.


:hugs: Look forward for your comments and improvements! :hugs: