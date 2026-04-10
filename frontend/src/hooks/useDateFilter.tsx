import { useState, useCallback } from "react";

interface DateFilter {
  startDate: Date | null;
  endDate: Date | null;
}

interface UseDateFilterReturn {
  dateFilter: DateFilter;
  setDateFilter: (filter: DateFilter) => void;
  setStartDate: (date: Date | null) => void;
  setEndDate: (date: Date | null) => void;
  clearFilter: () => void;
  setPreset: (preset: "today" | "week" | "month" | "year") => void;
  isInRange: (date: Date) => boolean;
}

const PRESETS = {
  today: () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return { startDate: today, endDate: new Date() };
  },
  week: () => {
    const week = new Date();
    week.setDate(week.getDate() - 7);
    return { startDate: week, endDate: new Date() };
  },
  month: () => {
    const month = new Date();
    month.setMonth(month.getMonth() - 1);
    return { startDate: month, endDate: new Date() };
  },
  year: () => {
    const year = new Date();
    year.setFullYear(year.getFullYear() - 1);
    return { startDate: year, endDate: new Date() };
  },
};

export function useDateFilter(): UseDateFilterReturn {
  const [dateFilter, setDateFilter] = useState<DateFilter>({
    startDate: null,
    endDate: null,
  });

  const setStartDate = useCallback((date: Date | null) => {
    setDateFilter((prev) => ({ ...prev, startDate: date }));
  }, []);

  const setEndDate = useCallback((date: Date | null) => {
    setDateFilter((prev) => ({ ...prev, endDate: date }));
  }, []);

  const clearFilter = useCallback(() => {
    setDateFilter({ startDate: null, endDate: null });
  }, []);

  const setPreset = useCallback((preset: keyof typeof PRESETS) => {
    setDateFilter(PRESETS[preset]());
  }, []);

  const isInRange = useCallback(
    (date: Date) => {
      if (!dateFilter.startDate && !dateFilter.endDate) return true;

      const d = new Date(date);
      if (dateFilter.startDate && d < dateFilter.startDate) return false;
      if (dateFilter.endDate && d > dateFilter.endDate) return false;
      return true;
    },
    [dateFilter]
  );

  return {
    dateFilter,
    setDateFilter,
    setStartDate,
    setEndDate,
    clearFilter,
    setPreset,
    isInRange,
  };
}

interface DateRangePickerProps {
  dateFilter: DateFilter;
  onFilterChange: (filter: DateFilter) => void;
  onClear: () => void;
}

export function DateRangePicker({
  dateFilter,
  onFilterChange,
  onClear,
}: DateRangePickerProps) {
  const hasFilter = dateFilter.startDate || dateFilter.endDate;

  const formatDate = (date: Date | null) => {
    if (!date) return "";
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      {/* Preset buttons */}
      <div className="flex items-center gap-1">
        {(["today", "week", "month", "year"] as const).map((preset) => (
          <button
            key={preset}
            onClick={() => onFilterChange(PRESETS[preset]())}
            className="px-2 py-1 text-xs bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 capitalize"
          >
            {preset}
          </button>
        ))}
      </div>

      {/* Current filter display */}
      {hasFilter && (
        <div className="flex items-center gap-2 px-2 py-1 bg-secondary rounded">
          <span className="text-muted-foreground">
            {formatDate(dateFilter.startDate)} - {formatDate(dateFilter.endDate)}
          </span>
          <button
            onClick={onClear}
            className="p-0.5 text-muted-foreground hover:text-foreground"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
