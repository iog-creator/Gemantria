import { useState, useEffect } from "react";

interface BrowserVerificationData {
    ok: boolean;
    checks?: {
        ok_browser?: boolean;
        ok_index?: boolean;
        ok_catalog?: boolean;
        ok_compliance_summary?: boolean;
        ok_violations?: boolean;
        ok_guard_receipts?: boolean;
        endpoints_count?: number;
    };
    screenshots?: {
        index?: string;
        catalog?: string;
        compliance_summary?: string;
        violations?: string;
        guard_receipts?: string;
    };
}

export default function BrowserVerifiedBadge() {
    const [data, setData] = useState<BrowserVerificationData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch("/exports/evidence/webproof/report.json");
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                    setError(null);
                } else {
                    setError("Browser verification data not available");
                }
            } catch (err) {
                setError("Failed to load browser verification data");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Poll every 60s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-100 text-gray-600 text-sm">
                <span className="w-2 h-2 rounded-full bg-gray-400 animate-pulse" />
                Browser Verification: Loading...
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-gray-100 text-gray-600 text-sm">
                <span className="w-2 h-2 rounded-full bg-gray-400" />
                Browser Verification: Unavailable
            </div>
        );
    }

    const isVerified = data.ok === true;
    const verifiedPages = data.checks
        ? Object.values(data.checks).filter((v) => v === true).length
        : 0;
    const screenshotCount = data.screenshots ? Object.keys(data.screenshots).length : 0;

    const badgeColor = isVerified
        ? "bg-green-100 text-green-800 border-green-200"
        : "bg-yellow-100 text-yellow-800 border-yellow-200";

    return (
        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md border ${badgeColor} text-sm`}>
            <span className={`w-2 h-2 rounded-full ${isVerified ? "bg-green-500" : "bg-yellow-500"}`} />
            <span className="font-medium">Browser-Verified</span>
            <span className="text-xs opacity-75">
                ({verifiedPages} page{verifiedPages !== 1 ? "s" : ""}, {screenshotCount} screenshot
                {screenshotCount !== 1 ? "s" : ""})
            </span>
            {data.screenshots && Object.keys(data.screenshots).length > 0 && (
                <a
                    href="/exports/evidence/webproof"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-xs underline opacity-75 hover:opacity-100"
                    title="View verification screenshots"
                >
                    View Screenshots
                </a>
            )}
        </div>
    );
}

