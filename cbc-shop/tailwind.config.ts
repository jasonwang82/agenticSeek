import type { Config } from "tailwindcss";

const config: Config = {
	content: ["./src/**/*.{ts,tsx}"],
	theme: {
		extend: {
			colors: {
				brand: {
					beige: "#E8E1D9",
					deepblue: "#0B2545",
				},
			},
		},
	},
	plugins: [],
};

export default config;