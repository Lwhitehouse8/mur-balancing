# MUR Balancing for Dummies

Step-by-step photo guide for setting up and babysitting tractive battery balancing, plus a balance tracker. For Elec HV trained members only.

The whole site is the single `index.html` file, with the photos and readings built in. It's hosted with GitHub Pages from the `main` branch.

Live site: https://lwhitehouse8.github.io/mur-balancing/

## How the tracker stores readings

- All shared readings live in `readings.csv` (time, high, low, avg, note).
- **Add reading** on the Tracking tab opens a pre-filled GitHub issue. Pressing **Create** runs `.github/workflows/add-reading.yml`, which checks the numbers, adds the row to `readings.csv`, closes the issue with a reply and redeploys the site. Anyone logging readings needs a GitHub account.
- Readings that haven't been shared yet stay on that device and show as "Not shared yet" with a **Share** link.
- To fix or remove a reading, edit `readings.csv` directly on GitHub.
- The Assumptions panel (capacity, resistor, hours) is saved per device.
