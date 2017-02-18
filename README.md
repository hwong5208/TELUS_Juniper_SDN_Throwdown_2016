# TelusJuniperThrowdown
Telus Throwdown 2016

  This script is a project that was presented at the Telus Throwdown 2016 at the Telus Garden.
  This event started on Wednesday July 20th to Tuesday July 26th.
  
  This project utlizes:
    NorthStar API provided by Junpier, allowing for centralized control for LSPs.
    Redis, for subscription notifications of Link Failures.
  
  The main Script is /src/configurable_autoSwitch.py
    It contains a configurable configuration that is easily changed using the static variables placed at the top of the file.
    
  Main features:
    Automated Switching of LSP
      * LSP routes change automatically on detection of Link Faliure that affects the LSP.
    Redis Event Subscription
      * Active notifcation of link failures.
    Static path
      * Allows for low resource and quick switching of LSPs, as it is not dependant on the server finishing a calculation.
    Ease of configurability
      * All configurations needed to deploy tool is placed at the top of the file.
