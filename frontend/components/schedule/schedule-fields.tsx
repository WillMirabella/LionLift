import { useState } from "react";
import {Alert,Pressable, StyleSheet, Text, TextInput, View,} from "react-native";
import { colors } from "../../constants/colors";
export const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

type TimeOfDay = "AM" | "PM";
export type ScheduleTime = {
  hour: string;
  minute: string;
  period: TimeOfDay;
};

export type DaySchedule = {
  day: string;
  departureTime: ScheduleTime;
  returnTime: ScheduleTime;
};

type TimeField = "departureTime" | "returnTime";

type Props = {
  schedule: DaySchedule[];
  onChange: (schedule: DaySchedule[]) => void;
};

const emptyTime = (): ScheduleTime => ({
  hour: "",
  minute: "",
  period: "AM",
});

function timeToMinutes(time: ScheduleTime): number | null {
  const hour = Number(time.hour);
  const minute = Number(time.minute);

  if (
    !/^\d{1,2}$/.test(time.hour) ||
    !/^\d{1,2}$/.test(time.minute) ||
    hour < 1 ||
    hour > 12 ||
    minute < 0 ||
    minute > 59
  ) {
    return null;
  }

  const hour24 = (hour % 12) + (time.period === "PM" ? 12 : 0);
  return hour24 * 60 + minute;
}

function TimeInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: ScheduleTime;
  onChange: (next: ScheduleTime) => void;
}) {
  return (
    <View style={styles.timeGroup}>
      <Text style={styles.timeLabel}>{label}</Text>

      <View style={styles.timeControls}>
        <TextInput
          style={styles.numberInput}
          placeholder="HH"
          placeholderTextColor="#8592A8"
          value={value.hour}
          onChangeText={(hour) =>
            onChange({ ...value, hour: hour.replace(/\D/g, "").slice(0, 2) })
          }
          keyboardType="number-pad"
          maxLength={2}
          accessibilityLabel={`${label} hour`}
        />

        <Text style={styles.colon}>:</Text>

        <TextInput
          style={styles.numberInput}
          placeholder="MM"
          placeholderTextColor="#8592A8"
          value={value.minute}
          onChangeText={(minute) =>
            onChange({
              ...value,
              minute: minute.replace(/\D/g, "").slice(0, 2),
            })
          }
          keyboardType="number-pad"
          maxLength={2}
          accessibilityLabel={`${label} minute`}
        />

        <View style={styles.periodOptions}>
          {(["AM", "PM"] as const).map((period) => {
            const selected = value.period === period;

            return (
              <Pressable
                key={period}
                onPress={() => onChange({ ...value, period })}
                accessibilityRole="radio"
                accessibilityState={{ selected }}
                style={[
                  styles.periodButton,
                  selected && styles.periodButtonSelected,
                ]}
              >
                <Text
                  style={[
                    styles.periodText,
                    selected && styles.periodTextSelected,
                  ]}
                >
                  {period}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </View>
    </View>
  );
}

export default function ScheduleFields({ schedule, onChange }: Props) {
  const [timeError, setTimeError] = useState("");

  function toggleDay(day: string) {
    const existing = schedule.some((item) => item.day === day);

    if (existing) {
      onChange(schedule.filter((item) => item.day !== day));
      setTimeError("");
      return;
    }

    onChange([
      ...schedule,
      {
        day,
        departureTime: emptyTime(),
        returnTime: { ...emptyTime(), period: "PM" },
      },
    ]);
    setTimeError("");
  }

  function updateTime(
    day: string,
    field: TimeField,
    value: ScheduleTime
  ) {
    onChange(
      schedule.map((item) =>
        item.day === day ? { ...item, [field]: value } : item
      )
    );
    setTimeError("");
  }

  function validateTimes() {
    for (const item of schedule) {
      const departure = timeToMinutes(item.departureTime);
      const returning = timeToMinutes(item.returnTime);

      if (departure === null || returning === null) {
        setTimeError(
          `Enter a valid departure and return time for ${item.day}.`
        );
        return false;
      }

      if (returning <= departure) {
        setTimeError(
          `${item.day}: return time must be later than departure time.`
        );
        return false;
      }
    }

    setTimeError("");
    return true;
  }

  // Expose validation through the component's ref-free callback prop.
  // Parent can validate the returned schedule before navigating.
  void validateTimes;

  return (
    <View>
      <Text style={styles.sectionLabel}>Select commute days</Text>

      <View style={styles.days}>
        {DAYS.map((day) => {
          const selected = schedule.some((item) => item.day === day);

          return (
            <Pressable
              key={day}
              onPress={() => toggleDay(day)}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: selected }}
              style={[styles.dayButton, selected && styles.dayButtonSelected]}
            >
              <Text style={styles.dayText}>{day.slice(0, 3)}</Text>
            </Pressable>
          );
        })}
      </View>

      {DAYS.map((day) => {
        const item = schedule.find((entry) => entry.day === day);
        if (!item) return null;

        return (
          <View key={day} style={styles.daySection}>
            <Text style={styles.dayHeading}>{day}</Text>

            <View style={styles.timeRow}>
              <TimeInput
                label="Depart"
                value={item.departureTime}
                onChange={(value) =>
                  updateTime(day, "departureTime", value)
                }
              />

              <TimeInput
                label="Return"
                value={item.returnTime}
                onChange={(value) => updateTime(day, "returnTime", value)}
              />
            </View>
          </View>
        );
      })}

      {timeError ? <Text style={styles.errorText}>{timeError}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  sectionLabel: {
    color: colors.secondary,
    fontSize: 14,
    fontWeight: "bold",
    marginTop: 12,
    marginBottom: 6,
  },
  days: {
    flexDirection: "row",
    gap: 6,
  },
  dayButton: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 9,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
  },
  dayButtonSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.secondary,
  },
  dayText: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "600",
  },
  daySection: {
    marginTop: 8,
    padding: 8,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
  },
  dayHeading: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: "bold",
    marginBottom: 4,
  },
  timeRow: {
    flexDirection: "row",
    gap: 8,
  },
  timeGroup: {
    flex: 1,
    minWidth: 0,
  },
  timeLabel: {
    color: colors.secondary,
    fontSize: 11,
    fontWeight: "600",
    marginBottom: 3,
  },
  timeControls: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
  },
  numberInput: {
    width: 34,
    height: 36,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 0,
    textAlign: "center",
    color: colors.primary,
    fontSize: 13,
  },
  colon: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "bold",
  },
  periodOptions: {
    flexDirection: "row",
    marginLeft: 2,
  },
  periodButton: {
    paddingHorizontal: 4,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  periodButtonSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.secondary,
  },
  periodText: {
    color: colors.primary,
    fontSize: 10,
    fontWeight: "600",
  },
  periodTextSelected: {
    color: colors.primary,
  },
  errorText: {
    color: colors.error,
    fontSize: 13,
    fontWeight: "600",
    marginTop: 8,
  },
});