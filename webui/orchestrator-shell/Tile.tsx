import React from "react";

export type TileStatus = "healthy" | "degraded" | "offline" | "unknown";

export interface TileProps {
    id: string;
    title: string;
    status: TileStatus;
    reason?: string;
    onClick?: () => void;
    isExpanded?: boolean;
    children?: React.ReactNode;
    className?: string;
}

export default function Tile({
    id,
    title,
    status,
    reason,
    onClick,
    isExpanded = false,
    children,
    className = "",
}: TileProps) {
    const getStatusColor = (status: TileStatus) => {
        switch (status) {
            case "healthy":
                return "bg-green-500";
            case "degraded":
                return "bg-yellow-500";
            case "offline":
                return "bg-red-500";
            default:
                return "bg-gray-500";
        }
    };

    const getStatusBadgeColor = (status: TileStatus) => {
        switch (status) {
            case "healthy":
                return "bg-green-100 text-green-800";
            case "degraded":
                return "bg-yellow-100 text-yellow-800";
            case "offline":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    const baseClasses = `tile ${className}`.trim();

    return (
        <div
            className={baseClasses}
            onClick={onClick}
            role={onClick ? "button" : undefined}
            tabIndex={onClick ? 0 : undefined}
            onKeyDown={onClick ? (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onClick();
                }
            } : undefined}
            aria-label={onClick ? `Expand ${title} tile` : undefined}
        >
            <div>
                <div className="flex items-center gap-2 mb-2">
                    <div
                        className={`status-dot ${status}`}
                        aria-label={`Status: ${status}`}
                    />
                    <h3>{title}</h3>
                </div>
                {status === "unknown" && (
                    <p className="text-sm text-gray-400 mt-2">
                        When {title.toLowerCase()} health exports are available, this tile will show live status.
                    </p>
                )}
                {children && (
                    <div className="mt-3">
                        {children}
                    </div>
                )}
            </div>
        </div>
    );
}

