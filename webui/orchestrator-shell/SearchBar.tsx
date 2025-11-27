import React, { useState, useRef } from 'react';

interface SearchBarProps {
    onSearch: (query: string) => void;
    disabled?: boolean;
    placeholder?: string;
    initialValue?: string;
    debounceMs?: number;
}

export default function SearchBar({
    onSearch,
    disabled = false,
    placeholder = "Search...",
    initialValue = "",
    debounceMs = 300
}: SearchBarProps) {
    const [value, setValue] = useState(initialValue);
    const debounceTimeoutRef = useRef<any | null>(null);

    // Handle Enter key press - trigger search immediately
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !disabled && value.trim()) {
            // Clear any pending debounce
            if (debounceTimeoutRef.current) {
                clearTimeout(debounceTimeoutRef.current);
                debounceTimeoutRef.current = null;
            }
            // Trigger search immediately
            onSearch(value);
        }
    };

    return (
        <div className="relative w-full">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ width: '20px', height: '20px', flexShrink: 0 }}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
            <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm disabled:bg-gray-100 disabled:text-gray-500"
                placeholder={placeholder}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
            />
            {value && !disabled && (
                <button
                    onClick={() => {
                        setValue('');
                        onSearch('');
                    }}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ width: '20px', height: '20px', flexShrink: 0 }}>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            )}
        </div>
    );
}
