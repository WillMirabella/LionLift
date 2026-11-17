import { View, StyleSheet, Text, FlatList, TouchableWithoutFeedback, Pressable } from "react-native";
import { colors } from "../../constants/colors";
import { usePanGesture, GestureDetector, GestureHandlerRootView, Gesture, Touchable } from 'react-native-gesture-handler';
import { useState } from "react";

var exampleSchedule = [[12, 15], [13, 16], [9, 18], null, [12, 13]];

export default function ComplexSchedule() {
  const startTime = 8; // 8 AM
  const endTime = 20; // 8 PM

  let dayTexts = ["M", "T", "W", "Th", "F"].map((day, index) => (
    <View key={index} style={styles.cell}>
      <Text style={styles.dayText}>{day}</Text>
    </View>
  ));

  let grid = [];

  // generate time slots for the flat list
  const timeLabels = [];
  for (let hour = startTime; hour <= endTime; hour++) {
    timeLabels.push({ id: hour, title: `${hour % 12 || 12}:00` + (hour < 12 ? " AM" : " PM") });
  }

  grid.push(
    <View key="timeColumn" style={styles.gridCol}>
      <FlatList
        data={timeLabels}
        scrollEnabled={false}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <View style={styles.labelGridCell}>
            <Text style={styles.timeText}>{item.title}</Text>
          </View>
        )}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );

  // generate grid cells for the flat list
  
  for (let dayIndex = 0; dayIndex < 5; dayIndex++) {
    const timeSlots = [];
    for (let hour = startTime; hour <= endTime; hour += 0.5) {
      timeSlots.push({ id: hour, filled: (exampleSchedule[dayIndex] && exampleSchedule[dayIndex]![0] <= hour && exampleSchedule[dayIndex]![1] > hour) });
    }

    let [slots, setSlots] = useState(timeSlots);

    const slotHeight = 15; // Height of each slot in pixels

    const handleTouchMove = (e: any) => {
      const slotIndex = Math.floor(e.nativeEvent.locationY / slotHeight);
      // Verify that the slotIndex is within bounds
      if (slotIndex >= 0 && slotIndex < slots.length) {
        const newSlots = [...slots];

        if (exampleSchedule[dayIndex] === null) {
          exampleSchedule[dayIndex] = [slotIndex, slotIndex]; // Initialize the schedule for this day
          newSlots[slotIndex].filled = true; // Fill the touched slot
        } else {
          // the following two conditions handle expanding the schedule
          if (slotIndex > exampleSchedule[dayIndex]![1]) {
            for (let i = exampleSchedule[dayIndex]![0]; i <= slotIndex; i++) {
              newSlots[i].filled = true;
            }
            exampleSchedule[dayIndex]![1] = slotIndex; // Update the end time of the schedule
          } 
          else if (slotIndex < exampleSchedule[dayIndex]![0]) {
            for (let i = slotIndex; i < exampleSchedule[dayIndex]![1]; i++) {
              newSlots[i].filled = true;
            }
            exampleSchedule[dayIndex]![0] = slotIndex; // Update the start time of the schedule
          }
        }

        setSlots(newSlots);
      }
    };

    grid.push(
      <Pressable 
        key={`day-${dayIndex}`} 
        style={styles.gridCol}
        onTouchMove={handleTouchMove}
        onTouchStart={handleTouchMove}
      >
        <FlatList
          data={slots}
          scrollEnabled={false}
          contentContainerStyle={styles.listContent}
          renderItem={({ item }) => (
            // pointerEvents="none" line is absolutely required or else the onTouch event will return the pointer event on this child view instead of the parent
            <View pointerEvents="none" style={item.filled ? styles.gridCellFilled : (dayIndex == 4 ? [styles.gridCellBordered, { borderRightWidth: 0 }] : styles.gridCellBordered)}/>
          )}
          keyExtractor={(item) => item.id.toString()}
        />
      </Pressable>
    );
  }

  return (
    <View style={ styles.schedule }>
      <View style={ [styles.row, { paddingBottom: 5 }] }>
        <View style={{ flex: 1 }} />
        {dayTexts}
      </View>
      <View style={ styles.row }>
        {grid}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  schedule: {
    flex: 1,
    backgroundColor: colors.background,
  },
  row: {
    flexDirection: "row",
    backgroundColor: colors.background,
  },
  cell: {
    flex: 1,
    alignContent: "center",
    justifyContent: "center",
  },
  dayText: {
    color: colors.secondary,
    fontSize: 18,
    fontWeight: "bold",
    textAlign: "center",
  },
  timeText: {  
    color: colors.secondary,
    fontSize: 10,
    fontWeight: "500",
    textAlign: "right",
  },
  gridCol: {
    flex: 1,
    borderRightWidth: 1,
    borderRightColor: colors.border,
  },
  gridCellTopHalf: {
    flex: 1, 
    borderColor: colors.secondary,
    borderWidth: 1,
    padding: 0,
    margin: 0,
  },
  gridCellInside: {
    flex: 1, 
  },
  listContent: {
    flexGrow: 1,
  },
  labelGridCell: {
    height: 30,
    justifyContent: "center",
    paddingRight: 5,
  },
  gridCellBordered : {
    flex: 1,
    height: 15,
    borderColor: colors.border,
    borderBottomWidth: 1,
  },
  gridCellFilled: {
    flex: 1,
    height: 15,
    backgroundColor: colors.accent,
  }
});
