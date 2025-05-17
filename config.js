// config.js
// All the settings live here so we don't have to hunt through 8 different files

export const config = {
  // General app settings
  app: {
    port: 3000, // what port to run the server on
    debug: true, // toggle for extra logs, etc
  },

  // Camera config
  // need to install cam dependencies..
  // osx: brew install imagesnap
  // raspi: should be built in??
  camera: {
    // Driver.. 
    // could be "fswebcam" for raspi, "imagesnap" for macos
    // "gphoto2", or whatever tool we decide to support
    // device, "" blank on macos uses default camera
    // device "/dev/video0" is default raspicam
    driver: "imagesnap",
    device: "", // this might change on different systems raspi default /dev/video0
    resolution: "1280x720",
    delay: 1, // delay before capture (in seconds)
    outputFormat: "jpeg"
  },

  // Printer config
  printer: {
    enabled: true, // turn off printing without ripping it out
    name: "", // set your printer name here if needed (leave blank to use default)
    copies: 1, // default number of copies
    paperSize: "4x6", // just for documentation/logic, not used by lp directly
  },

  // File output paths
  paths: {
    captured: "captured/", // where photos go after they're taken
    templates: "templates/", // layout templates for arranging photos
    public: "public/", // for static assets
  }
};