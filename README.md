__**Item Catalog Project - Udacity Full Stack Web Developer Nanodegree**__

__Objective__

This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit, and delete their own items.

__Features__

    Checking authentication and authorization.
    CRUD support using SQLAlchemy and Flask.
    JSON endpoints.
    Implements oAuth using Google Sign-in API.


__Installation Instructions__

1. Download and inttall [Vagrant](https://www.vagrantup.com/) 

2. Download and install [VirtualBox](https://www.virtualbox.org/)

3. Download the Vagrant VM configuration from [here]([https://github.com/udacity/fullstack-nanodegree-vm)

4. Navigate to the directory where you placed the Udacity Virtual Machine and cd into the __/vagrant__ folder.

5. In the terminal, launch the virtual machine with __vagrant up__. 

6. Vagrant will now set up the VM and install necessary files.  This may take a while depending on the speed of your internet connection.  A reboot of your machine may be required to complete installation.

6. Once all files are insalled, navigate to the vagrant directory and enter __vagrant ssh__ to continue.    

7. Dowload this repository to your vagrant folder so it can be accessed on your VM.

__In your VM, navigate to your vagrant folder to perform the following setps__

8. Enter __python database_setup.py__ to setup the database.

9. Enter __python fake_db_with_users.py__ to setup the fake_users database.

10. To run the app, enter __python application.py__

11. Open http://localhost:8000/ in your favourite Web browser.

__Current Release__

v1.0 - Initial Release
v1.1 - cleaned up application.py to meet PEP8 Style Guidelines



