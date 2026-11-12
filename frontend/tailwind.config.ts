import type { Config } from "tailwindcss";
const config: Config = { content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"], theme: { extend: { colors: { ink: "#10213b", navy: "#173b68", mist: "#f5f8fc", line: "#e4ebf3", teal: "#07877f" }, boxShadow: { soft: "0 10px 30px rgba(16,33,59,.06)" } } }, plugins: [] };
export default config;
