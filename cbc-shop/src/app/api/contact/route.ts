import { NextResponse } from "next/server";

export async function POST(req: Request) {
	try {
		const body = await req.json();
		// TODO: integrate with email service (Resend/SendGrid). For now, stub success.
		if (!body?.email || !body?.message) {
			return NextResponse.json({ ok: false, error: "invalid" }, { status: 400 });
		}
		return NextResponse.json({ ok: true });
	} catch (e) {
		return NextResponse.json({ ok: false }, { status: 500 });
	}
}