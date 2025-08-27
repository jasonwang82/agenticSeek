export type Product = {
	id: string;
	name: string;
	description: string;
	price: number;
	sizes: string[];
	images: string[];
	tags: string[]; // e.g. ["new", "hot"]
};

export const products: Product[] = Array.from({ length: 12 }).map((_, i) => ({
	id: String(i + 1),
	name: `女装单品 ${i + 1}`,
	description: "简洁现代风格女装，灵感来自 Zara/H&M。",
	price: 199 + i * 10,
	sizes: ["XS", "S", "M", "L"],
	images: ["/placeholder"],
	tags: i < 4 ? ["new"] : i % 3 === 0 ? ["hot"] : [],
}));

export function getProductById(id: string) {
	return products.find((p) => p.id === id) || null;
}