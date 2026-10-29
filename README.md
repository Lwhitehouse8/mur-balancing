# MUR Balancing for Dummies

Step-by-step photo guide for setting up and babysitting tractive battery balancing, plus a balance tracker. For Elec HV trained members only.

The whole site is the single `index.html` file, with the photos and readings built in. It's hosted with GitHub Pages from the `main` branch.

The tracker shares readings through a Firebase Firestore database. The web config lives in `firebase-config.js` and the database rules in `firestore.rules`. Until the config is filled in, readings are saved only in the browser you add them from.

On first connect, the page loads the readings exported up to 29 Oct 2026 into the empty database. Any readings people saved on their own device before then get uploaded the next time they open the page.
