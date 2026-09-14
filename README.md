# Anchor: The only productivity app you'll EVER need

#### Video Demo: <URL https://youtu.be/ko0hGWaI9bQ>

#### Description:

Hi CS50 team and GitHub Lurkers, welcome to my ultimate productivity app -- Anchor!

Anchor is your best friend when it comes to actually finishing the goals you set out to achieve (and on time too hopefully!). With an in-built habit tracker and editor, alongside weekly reflections that track your progress and mental state. Think of it like Duolingo but for your habits, try and get as high a streak as you can!

Some future features to be added include:

- an AI assistant that will give you personalized plans and feedback on your habits and goals by tracking your habit completion rates and daily reflections.
- a way to add quantifiable metrics to your habits so instead of simply noting a habit as being completed for the day you can track what you specifically accomplished on that day.
- many many more to come.

#### Features

1. **Add/Edit Habits**

   Anchor features methods to add habits (title and start date are required but the rest are optional). Additionally, you can edit pre-existing habits if your goals end up changing.
   - Habits also feature a tracking feature (similar to streaks in Duolingo)

2. **Add Reflections**

   Reflections act as an alternative way to record your progress besides streaks. Reflections require a title, description, and date.
   - Your past reflections are visible at the bottom of the create reflections section.

3. **View Your Progress and Timeline**

   The coolest feature by far, the goal timeline features a calendar table that automatically resizes to the range of your habit and reflections. Habits also show their completion logs through empty (meaning not completed on that day) and full (marked as completed) circles
   - New rows are created for each habit to ensure no overlap or confusion occurs

<br>
<br>

#### The Code Behind it All

**1. Architecture | Electron + Flask**

As I mainly practice web development skills in CS50 (HTML/CSS/JS + FLASK + PYTHON), I wanted to hone in on those skills through my final project. But I also wanted to build something that does not need to depend solely on the internet and web, so I decided to build a Windows app instead using Electron.

Firstly, similar to a regularly run Python web server, Flask helps run the whole backend entirely on the users own machine to handle data logging, rendering pages and validating login sessions. Electron acts as the desktop application shell that opens a native Window and starts the Flask server.

Electron relies on two things to complete its role as a shell: Chromium and Node.js. Node.js (main.js in my project files) creates the app Window, starts and stops the flask server, and controls other app controls (i.e. minimize, quit, etc.) The Chromium browser Window is what loads and displays Flask's pages (login, register, habits) by pointing at Flask's local URL.

**2. Backend dev**

**a. Habits tracking**

The logic behind tracking habits actually stems from the exact logic I used to track stock purchases in my finance project for Pset 9. I even borrowed the idea for a habit_logs table in SQLite3 from my transactions table in my finance project. For my main habit tables I included important headings such as colour of the habit (for colour coding later on), start date (mandatory), end date (not mandatory), and etc. Importantly for each table I have a primary autoincrementing key so that it is simple to link tables together and find relationships.

Adding and editing habits is also relatively easy as I can just create HTML forms and then pull the answers and INSERT/UPDATE my tables. What was hard was creating a delete button as I needed to submit the form, delete the habit, then refresh the page so the habit disappeared. I also needed to implement a "confirm deletion" popup so that misclicks would be prevented. This was harder than I expected to implement so I took a shortcut and used an inline JavaScript shortcut versus redesigning my popup notification logic to check for confirmations. Although this leads to a confirmation popup that does not match the theme of my app, the time it saves and relatively small impact that it has on the user experience was worth it.

**b. Habit streaks**

Habit streaks was surprisingly hard to implement as I had to create a logic system that could parse through habit_logs to check completed_date and keep going until it sees a gap in the "completed_date"s. But this obviously creates the problem where there is no buffer time for checking completion dates, so if the user has not marked a habit as completed for the day, get_streak() will always return 0 no matter how long a streak the user had before.

This leads to errors where my UI shows "0 day streak" even though they have not lost the streak yet. This will be fixed in the future, and, by my guess, involves adding a buffer system that skips the checking "today" to give the user time to complete their habit.

**c. Reflections**

Basically the same logic as habits where I take user input through a form in HTML, then INSERT that into my SQLite3 table and return that to the page. One key difference is that I load the user's past reflections in the same page that the user adds reflections in and these past reflections are ordered by date DESC.

I also added a "empty state" checker using jinja if conditions so that if the user has no reflections (or no habits in habit.html), then the page will generate an empty box telling the user to "add your first reflection/habit".

**d. Goal timeline**

In terms of logic, definitely the hardest feature I added to Anchor.

Firstly, I had to plan out the way in which I would represent my timeline. I wanted to have my habits/reflections organized by date so I decided on a grid in which the first row would be the dates (starting from the earliest start date out of all user inputs and ending on the latest end date out of all user inputs), then each row after that would be individual habits or reflections. I also defined a cell width and label width to my grid so that everything would be spaced equally.

Secondly, in my actual logic I first extracted all the information about habits and reflections that I had, making sure to add dict(r) to everything so that I dont get SQLite3.Row objects that are read only but actual dictionaries. In the end this means that I get a list of dictionaries that I can iterate through.

Thirdly, I pulled all the "date" values from my 3 lists of dictionaries and created a list of all the dates, inclusive of both ends. I also needed to generate the date_headers list which I needed a day and month_label if and only if the day is the first of the month or the first in the list.

Additionally, I also wanted to represent habit streaks and completions into my timeline so I created dictionaries containing (habit_id, date) pairs (something similar was done for reflections). This means that in my "timeline.html" I can show which habits were completed on which days.

Finally, I pass in everything to build two lists of dicts that automatically store the date of the habit completed/reflection and the title so that my "timeline.html" can just iterate through the list and dynamically update the grid.

Finally finally, pass everything in, and voila!

**e. Status notification popups**

My implementation is pretty simple as there are only three options to choose from (the text, the redirect_url, and the colour.) It uses the flash system, do flash() in Python stores the message and colour in the user session, then when get_flashed_messages() is pulled in my layout.html it retrieves the message, colour pair (and also empties it).

In the future I plan to add a feature to add interactability to these notifications and hopefully also add OS notifactions.

**f. Authentication**

Firstly, for passwords I use a classic Werkzeug password hash (similar to what the CS50 team did for Pset 9 Finance) so that passwords are never stored as plain text.

Secondly, flask session writers a signed cookie that identifies the user. This cookie is cryptographically signed using SECRET_KEY (an environment variable that I created myself) so that it can't be tampered with client-side.

Lastly, I also decided to implement CSRF protection so that every single form includes a hidden-from-view CSRF token. This specifically prevents Cross-Site Request Forgery where a malicious site tricks a useres browser into submitting a request to Anchor.

<br>

**3. Frontend dev**

**a. Tailwind CSS, fonts, and alpine.js**

Font is Inter (which I self host).

Decided to use Tailwind CSS instead of regular CSS classes for my static visual design. Helps with creating an actual design system with themes instead of creating individual CSS classes for everything. Tailwind also helps a lot with consistency as there is no need to remember CSS class names as I can compose my style by combining multiple pre-made primitives that comes built in to Tailwind CSS. Overall, I chose to use Tailwind because it provides increased consistency, professionalism, and is just easier to use than creating hundreds of CSS classes.

Although Tailwind CSS is very good for static visual design, it does not have functionality for an interactive layer. That's where Alpine.js comes in. Alpine.js allows me to handle small pieces of behaviour that benefit to the interactability of my app. It helps with showing/hiding, toggling, and responding to clicks without needing a full JS framework.

**b. layout.html**

As I wanted to keep Anchor as professional as possible and I did not trust my website designing skills I found a free to use homepage template online through pixelcave (https://github.com/pixelcave/pixelcave.com-freebies). I took the template then removed unnecessary parts, trimmed down others, changed the spacing, and added a flashing notificaction system to create "layout.html". This acts as the base for all of my other webpages as it holds my navbar and the contact information at the bottom. THe rest of the template got transported to "index.html" and I adjusted some sections to better match my app.

You may see some currently useless blocks of space that just hold miscellaneous text right now, but in the future they will all have their own added functionality.

**c. Media**

Hehe, all media (the single photo on the homepage) is all hand drawn by yours truly!

---

Anyway that concludes the description of all the important features and components of my app, Anchor.

This was very fun and I learned a lot, thank you CS50 team and Davd J. Malan!!!!