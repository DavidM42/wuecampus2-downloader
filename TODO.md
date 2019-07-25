# Functionality to add
* Get files as stream to make runnable in lambda and stream into s3 and stream into zip to serve
* Files in moodle folders like PySql in swt https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=32329
* Add in that you can enter a course link and password to sign up for this course to auto sign up course,download and leave course again
* Method to quickly download everything from all courses of your logged in user
* Get first course at start before logging in
    * This will lead to login page
    * Get anchor and pass to login function
    * After login will be redirected to course page and download files of login
    * To save one request maybe
* create branch to autorun on aws and download all files to s3 to archive
    * and create second project with flask to give all files in simple interface for me
    * and eventually auto uploader to ereader or
    * anki auto card creator
    * fire tv adb uploader with directory structure for learning
    * basically create unified interface to build clients to bring pdfs to all devices
* Save cookies at __del_ of moodler class into pickle to reload on next use, try to save some logins on reruns
