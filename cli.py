from Moodler import Moodler
import sys

if __name__ == "__main__":
    if len(sys.argv) > 2:
        if len(sys.argv[1]) == 0:
            print("Enter a name for the course to name the folder this")
            quit()
        elif "https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=" not in sys.argv[2]:
            print("Malformed url; needs to look like https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=12345")
            quit()

        folder = sys.argv[1]
        url = sys.argv[2]

        m = Moodler()
        m.rip_course(url, folder+"/")
    else:
        print("Not enough arguments; use like:")
        print("python cli.py statistik2Vorlesung https://wuecampus2.uni-wuerzburg.de/moodle/course/view.php?id=123456")
    