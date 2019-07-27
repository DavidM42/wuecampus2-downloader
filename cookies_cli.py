from Moodler import Moodler 

from Moodler import Moodler
import sys

if __name__ == "__main__":
    if len(sys.argv) > 3:
        if len(sys.argv[1]) == 0:
            print("Enter a name for the course to name the folder this")
            quit()
        elif "https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=" not in sys.argv[3]:
            print("Malformed url; needs to look like https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=12345")
            quit()
        elif len(sys.argv[2]) == 0:
            print("Enter the content of your current MoodleSession Cookie as 2nd Parameter")
            quit()

        folder = sys.argv[1]
        cookie = sys.argv[2]
        url = sys.argv[3]

        m = Moodler(cookie)
        m.rip_course(url, folder+"/")
    else:
        print("Not enough arguments; use like:")
        print("python cli.py statistik2Vorlesung contentOfMoodleSessionCookie https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=123456")
    