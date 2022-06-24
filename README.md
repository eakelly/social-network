# social-network

## Team Members: Elizabeth Kelly and Krithika Prakash

## Setup
You will need to store the Postgres username and password in a `config/config.json` file. You can do so by running the command below, replacing `<username>` and `<password>` with the provided credentials in the project submission.
```
echo '{"user":"<username>", "password":"<password>"}' >> config/config.json
```


## Entities/Relationships/Operations implemented:
### Users:
- CREATE: Users can signup using the provided form. First name, Last name and age are required inputs. Users must be at least 13 years old. Any missing required field will result in an error being displayed.
- READ:  Existing users can login using userid and password. Note: We have created an admin user with user id=0, password is 123456.  There are also other users with ids 1 to 10, all with password 1234.  If user id or password is invaid,user is redirected to login again along with an error display. 

### Profiles:
- CREATE/ READ: When a user signs up, a default profile is automatically created  (by the database trigger functions). After login, the user is placed in the user_info page where he can see all the details related to him, such as his Name, Age, Places he has lived in, his Friends, his profiles, and his posts. Note that admin user are taken to an admin page where he can access admin-only information such as locations.
- UPDATE: User can edit his profile details with a new bio. Any special characters in the bio will result in an error being displayed. Bio is optional for a profile.

### Located_in:
- READ: In each user profile, we display the list of all places that he/she has lived in. 

### Posts:
- CREATE: Users create new posts by filling in the form. Note that each post is associated with a specific profile of that user. Hence user must specific the profile-id along with the post content when creating new posts
- DELETE:  All posts created by this user are displayed and user can delete a specific POST by clicking on the Delete link.

### Locations:
- READ: As an admin user (id 0, pw:123456) , you can see all the locations that were made available for users to select.

### Friends:
- READ: Each user profile, displays the list of users who are their friends.

## SQL Injection Prevention
	We have implemented parameter binding to prevent this in both form and url parameters.

## Entities/Relationships/Operations not implemented:
We have implemented all the entities and relationships with atleast one operation. However we haven’t yet implemented all the CRUD operations for all the entities. Some of the operations such as remove user, add new location, add new friends, etc,... do not have an interface in the web application. 

## Changes since Part 1 and Part 2:
We have added “password” attribute to the users table to implement the login functionality. The password must be of length 4 or greater.
First, middle, and last name should not have special characters or numbers
We have also added an admin user with id 0

## Most Interesting DB operations:
The admin_page has some really interesting operations where it shows the statistics of the social network. One of the queries dynamically accepts a state location from a drop down list and filters all users from that state. Combines information from located_in, locations, and users tables.

The admin_page also shows the average age of all friends for each user. This query groups by user_ids to find all of a user’s friends and then calculates the average age of all their friends. In addition, the admin_page also shows the average number of posts for users above the age of 30 and at or under the age of 30. Another feature of the admin_page is that we can view users by their locations.

The user_info page and the user_profile pages have the most interesting database operations of the entire application. For the user_info page, we display all the user’s locations, friends, posts, and a list of all the profiles they created. For the user_profile page, we show all the posts made by the user for that specific profile and any other profile information that they added.
