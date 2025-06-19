import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { query } = await req.json();

    if (!query) {
      return NextResponse.json({ error: "Missing query" }, { status: 400 });
    }

    const NLP_SERVICE_URL = process.env.NLP_SERVICE_URL || "http://localhost:8000";

    const upstreamRes = await fetch(`${NLP_SERVICE_URL}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!upstreamRes.ok) {
      console.error("Upstream error", await upstreamRes.text());
      return NextResponse.json({ error: "NLP service error" }, { status: 502 });
    }

    const data = await upstreamRes.json();

    return NextResponse.json(data);
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
} 