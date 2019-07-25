import requests
from bs4 import BeautifulSoup
from time import sleep as wait_request
import os
from configparser import ConfigParser, NoOptionError, NoSectionError
from zipfile import ZipFile 
from re import compile as re_compile
from random import uniform

import unicodedata
import string

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    #Thanks to https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8

    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    
    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit] 

class CampusFile():
    def __init__(self, name, url, section_title=None):
        self.name = name        
        self.url = url
        self.section_title = section_title

class Moodler():
    def __init__(self):
        """
            Sets up base class variables
            Gets login info from auth.ini file
            Calls login method to handle login flow and update cookies
        """
        self.cookies = {}

        #for unified base path to not save sonstwo and include in .gitignore
        self.base_path = "downloads/"

        #can change to download faster/slower
        #used to not get account blocked/terminated
        self.download_wait_time = 0.4

        #TODO add other file icons for other types next to pdf/excel/jpeg
        # some examples for links but now only use ending and compare
        # self.file_thumbnail_links = [
        #     "https://wuecampus2.uni-wuerzburg.de/moodle/theme/image.php/fordson/core/1562689635/f/pdf",
        #     "https://wuecampus2.uni-wuerzburg.de/moodle/theme/image.php/fordson/core/1562689635/f/spreadsheet",
        #     "https://wuecampus2.uni-wuerzburg.de/moodle/theme/image.php/fordson/core/1562689635/f/jpeg",
        #     "https://wuecampus2.uni-wuerzburg.de/moodle/theme/image.php/fordson/core/1563800556/f/pdf"
        # ]
        self.file_thumbnail_endings = [
            "pdf",
            "spreadsheet",
            "jpeg"
        ]

        #get login credentials from config and then login into moodle
        config = ConfigParser()
        config.read('auth.ini')

        try:
            self.username = config.get('wuecampus2', 'username')
            self.password = config.get('wuecampus2', 'password')
        except (NoOptionError,NoSectionError) as e:
            print(e)
            print("Malformed auth.ini file. Reference to original auth.ini.example for format")
            quit()

        self.__login()

    def __get_cookies_content(self):
        '''
            This method downloads the login page via GET to get up to date cookies
            and gets login form to return this html for login method to parse logintoken
        '''
        login_page_url = "https://wuecampus2.uni-wuerzburg.de/moodle/login/index.php"
        login_page_r = requests.get(login_page_url)
        content = login_page_r.content

        for c in login_page_r.cookies:
            if "BIGipServerPOOL_WueCampus2_443" in c.name:
                # print("new biggips pool")
                # print(c.name, c.value)
                self.cookies["BIGipServerPOOL_WueCampus2_443"] = c.value
            if "MoodleSession" in c.name:
                # print("new moodlesession")
                # print(c.name, c.value)
                self.cookies["MoodleSession"] = c.value

        return content

    def __login(self):
        login_soup = BeautifulSoup(self.__get_cookies_content(), "html.parser")
        try:
            logintoken = login_soup.find('input', {'name': 'logintoken'}).get('value')
            anchor = login_soup.find('input', {'name': 'anchor'}).get('value')
        except AttributeError as e:
            #TODO error handling
            print(e)
            quit()
            pass

        # print(logintoken)
        # print(anchor)

        login_post_url = "https://wuecampus2.uni-wuerzburg.de/moodle/login/index.php"
        post_parameters = {
            "anchor": anchor,
            "logintoken": logintoken,
            "username":	self.username,
            "password": self.password,
            "rememberusername": 1
        }

        # print("Pre post cookies:")
        # print(self.cookies)
        login_post_r = requests.post(login_post_url, data=post_parameters, cookies=self.cookies,allow_redirects=False)
        
        #TODO create requests library issue why following of 302 redirects on get/post does not update cookie header in between if receives new moodle session in response cookie on 302 response

        #now disabled redirects on login post to update cookies on first 302 redirect and then follow redirect to test session get
        for c in login_post_r.cookies:
            if "BIGipServerPOOL_WueCampus2_443" in c.name:
                # print("New bigserverpoll cookie:")
                # print(c.value)
                self.cookies["BIGipServerPOOL_WueCampus2_443"] = c.value
            if "MoodleSession" in c.name:
                # print("New moodlesession")
                # print(c.value)
                #update MoodleSession in cookie with new authenticated Session
                self.cookies["MoodleSession"] = c.value

        login_get_testsession_r = requests.get(login_post_r.url, cookies=self.cookies,allow_redirects=False)
        # print(login_get_testsession_r.content.decode("utf-8"))
        # print(login_get_testsession_r.url)
        # print(login_get_testsession_r.status_code)
        # print(login_get_testsession_r.cookies)

    def __logout(self):
        #TODO should method be deleted or should be used?
        #TODO untested
        logout_page_url = "https://wuecampus2.uni-wuerzburg.de/moodle/login/logout.php"
        logout_page_r = requests.get(logout_page_url, cookies=self.cookies)
        content = logout_page_r.content
        
        logout_soup = BeautifulSoup(content, "html.parser")
        try:
            sesskey = logout_soup.find('input', {'name': 'sesskey'}).get('value')
        except AttributeError as e:
            print(e)
            print("Probaly not logged in yet/anymore so can't log out")

        final_logout_url = "https://wuecampus2.uni-wuerzburg.de/moodle/login/logout.php?sesskey=" + str(sesskey)
        final_logout_r = requests.get(final_logout_url, cookies=self.cookies)
        # print(final_logout_r.status_code)
        # print(final_logout_r.url)

    def __download_file(self,url,path,filename, find_extension=True):
        #append path to classwide base path
        path = self.base_path + path
        
        #create path to file if not exists and then add filename to path
        os.makedirs(path, exist_ok=True)
        path += filename

        file_r = requests.get(url, cookies=self.cookies, allow_redirects=True)

        #cope with this a href link file workaround style thing https://wuecampus2.uni-wuerzburg.de/moodle/mod/resource/view.php?id=1120681 so have to parse again and follow
        if "view.php" in file_r.url:
            redirect_link_soup = BeautifulSoup(file_r.content, "html.parser")
            try:
                #Try to get another redirect in text on site
                parent_elem = redirect_link_soup.find('div', {'class': 'resourceworkaround'})
                href = parent_elem.find("a")["href"]
                file_r = requests.get(href, cookies=self.cookies, allow_redirects=True)
            except AttributeError as e:
                try:
                    #Try to get embededd image on page
                    img_elem = redirect_link_soup.find('img', {'class': 'resourceimage'})
                    file_r = requests.get(img_elem["src"], cookies=self.cookies, allow_redirects=True)
                except AttributeError as e:                    
                    print(e)
                    print("getting file "+ path + " failed")
                    return None
        
        print("Downloaded file: " + filename)

        #final redirect to resource contains file extension in path so get that now if unknown previously
        if find_extension:
            final_url = file_r.url
            file_extension = final_url.rpartition('.')[1] + final_url.rpartition('.')[2]
            path += file_extension

        #TODO catch failed gets like non existant or auth failed

        #https://stackoverflow.com/questions/34503412/download-and-save-pdf-file-with-python-requests-module
        try:
            with open(path, 'wb') as f:
                f.write(file_r.content)
        except OSError as e:
            print(e)
            #TODO error catching for incorect file names and so on


    def __zip_dir(self,course_path, zip_file_name):
        #append path to classwide base path
        dir_path = self.base_path + course_path
        
        #TODO remove?
        #create path to file if not exists and then add filename to path
        os.makedirs(dir_path, exist_ok=True)
        
        if not dir_path.endswith("/"):
            dir_path += "/"

        # setup file paths variable
        filePaths = []
        
        # Read all directory, subdirectories and file lists
        for root, directories, files in os.walk(dir_path):
            for filename in files:
                # Create the full filepath by using os module.
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
                
        # writing files to a zipfile
        zip_file = ZipFile(dir_path+zip_file_name+'.zip', 'w')
        with zip_file:
            # writing each file one by one
            for file in filePaths:
                #filter out .zip file as content as would be recursive
                if not file.endswith(".zip"):
                    #supply alternative path as which it gets saved in zip archive
                    #cuts out base path and course path directory to be it shorter
                    zip_file.write(file, file.replace(self.base_path, "").replace(course_path, ""))
            
        print(dir_path+zip_file_name+'.zip file was created successfully!')


    def rip_course_r(self, url, directory="files/"):
        if not directory.endswith("/"):
            directory += "/"

        course_r = requests.get(url, cookies=self.cookies, allow_redirects=True)
        content = course_r.content
        course_soup = BeautifulSoup(content, "html.parser")

        #recursively call itself with urls of all sub categories if there are any like stat2 tutorium course
        for link_element in course_soup.find_all('a', class_="section-go-link"):
            section_url = link_element["href"]
            print("Now getting section with url:")
            print(section_url)
            self.rip_course_r(section_url, directory)

        for file_type_ending in self.file_thumbnail_endings:
            #thanks to https://stackoverflow.com/a/45365599/7692491
            all_file_icon_elements = course_soup.find_all('img', {'src': re_compile(r".*"+file_type_ending)})

            #loops through thubmnail file link images, gets parent and name+url out of this element
            file_links = []
            for icon_elem in all_file_icon_elements:
                parent_elem = icon_elem.parent
                name = parent_elem.find("span").text

                #try to get parent element container and title of it for subdirs to add for structure
                #when fails just skip and save in base course path
                section_title = None
                try:
                    tmp_parent = parent_elem
                
                    while True:
                        tmp_parent = tmp_parent.parent
        
                        if tmp_parent is None:
                            #no parent found so probably could not find correct contents div to find out subdir section-title
                            print("could not find section tilte for file with name: "+ name)
                            break
                        elif not tmp_parent.has_attr('class'):
                            #parent has no classes so not the class searched for
                            continue
                        elif "content" in tmp_parent["class"]:
                            #section divs contain a h3 with a span in it with the title for this section so get this text for subdir name and exit loop
                            section_title = tmp_parent.find('h3', {'class': "sectionname"}).find("span").text
                            break
                except (AttributeError, KeyError) as e:
                    print(e)
                    print("could not find section title for file so will be in main dir; filename: " + name)

                #clean up name and section title to use as valid path to save file                
                name = clean_filename(name)
                section_title = clean_filename(section_title)

                url = parent_elem["href"]

                campus_file = CampusFile(name,url, section_title)
                file_links.append(campus_file)

            for wue_file in file_links:
                tmp_path = directory
                #use section title as subdir and append to path if section_title exists
                if wue_file.section_title is not None:
                    tmp_path += wue_file.section_title + "/"

                self.__download_file(wue_file.url, tmp_path ,wue_file.name)
                #not get banned time sleep
                variated_wait_time = uniform(self.download_wait_time-0.25, self.download_wait_time+0.25)
                wait_request(variated_wait_time)


    def rip_course(self, url, directory="files/"):
        self.rip_course_r(url,directory)
        self.__zip_dir(directory,"archive")
        print("Course was downloaded!")
    # def __del__(self):
    #     self.__logout()
