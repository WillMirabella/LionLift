import { View, StyleSheet, Text, FlatList } from "react-native";
import { colors } from "../../constants/colors";

const exampleSchedule = [[12, 15], [13, 16], [9, 18], null, [12, 13]];

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
  const timeSlots = [];
  for (let hour = startTime; hour <= endTime; hour++) {
    timeSlots.push({ id: hour, title: `${hour % 12 || 12}:00` + (hour < 12 ? " AM" : " PM") });
  }

  grid.push(
    <View key="timeColumn" style={styles.gridCol}>
      <FlatList
        data={timeSlots}
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
    const gridCells = [];
    for (let hour = startTime; hour <= endTime; hour += 0.5) {
      gridCells.push({ id: hour, filled: (exampleSchedule[dayIndex] && exampleSchedule[dayIndex]![0] <= hour && exampleSchedule[dayIndex]![1] > hour) });
    }
    // create a style with bottom and right borders for the grid cells, except for the last column and last row

    grid.push(
      <View key={`day-${dayIndex}`} style={styles.gridCol}>
        <FlatList
          data={gridCells}
          scrollEnabled={false}
          contentContainerStyle={styles.listContent}
          renderItem={({ item }) => (
            <View style={item.filled ? styles.gridCellFilled : (dayIndex == 4 ? [styles.gridCellBordered, { borderRightWidth: 0 }] : styles.gridCellBordered)}/>
          )}
          keyExtractor={(item) => item.id.toString()}
        />
      </View>
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
