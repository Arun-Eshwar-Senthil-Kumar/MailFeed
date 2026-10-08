module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: { extend: { colors: { ink: "#14181F", paper: "#F6F7F9", hot: "#FF4D2E", job: "#2F5BFF", due: "#F5A524" } } },
};
