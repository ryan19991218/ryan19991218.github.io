# Medinfo
#### Video Demo:  <URL HERE>
#### Description:
I am a medical student in Taiwan, and before entering clinical practice, there is a lot of information about physician recruitment and various medical conferences. However, due to the lack of a unified platform for different hospitals and units to publish information, the information obtained by students from different medical schools can vary significantly. Therefore, I hope to establish a website to allow students who have access to information to share it. The goal is to provide a more comprehensive and user-friendly interface for viewing event details, including time, location, hosting hospital, quota limits, etc.

Below is a brief introduction to the functionality of each file:

In app.py, various HTML websites are linked.

In helper.py, the functions "apology" and "login_required" are defined.

In pgydata.py, different event categories, medical specialties, and hospitals are included.

In rdata.py, there is additional information about different hospitals.

In medinfo.db, an SQL database contains various event and related information.

In requirements.txt, the required modules are listed.

In sample.txt, common commands for modifying medinfo.db in the backend are provided.

In the "template" folder:

- Index.html is the homepage.
- add.html is the interface for users to add events.
- history.html displays information about events already added to the database.
- your.html checks the user's identity and provides editing or deleting permissions.
- pgy.html shows the quota limits for PGY students in different hospitals.
- r.html displays the quota limits for Resident doctors in different specialties.
- modify.html allows users to modify data with the database as default values.

Other files such as apology.html, layout.html, login.html, and register.html are similar to the content covered in class.

In the "static" folder, you can find related CSS and image files, as well as the original files for quota limits. It also includes a folder for users to upload files named "file."