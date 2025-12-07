import React from "react";
import type { ModeId } from "../model/consoleConfig";

interface LeftNavProps {
    modes: ModeId[];
    activeMode: ModeId;
    onModeChange: (mode: ModeId) => void;
}

export const LeftNav: React.FC<LeftNavProps> = ({ modes, activeMode, onModeChange }) => {
    return (
        <nav className="left-nav">
            <h2 className="left-nav__title">Modes</h2>
            <ul className="left-nav__list">
                {modes.map((mode) => (
                    <li key={mode}>
                        <button
                            type="button"
                            className={`left-nav__button ${mode === activeMode ? "left-nav__button--active" : ""}`}
                            onClick={() => onModeChange(mode)}
                        >
                            {mode.charAt(0).toUpperCase() + mode.slice(1)}
                        </button>
                    </li>
                ))}
            </ul>
        </nav>
    );
};
