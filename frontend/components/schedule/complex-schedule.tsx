import { View, StyleSheet, Text } from "react-native";
import { colors } from "../../constants/colors";

const exampleSchedule = [[12, 15], [13, 16], [9, 18], null, [12, 13]];

export default function ComplexSchedule() {
  const startTime = 8; // 8 AM
  const endTime = 20; // 8 PM

  let timeTexts = []
  for (let i = startTime; i <= endTime; i++) {
    timeTexts.push(<View style={styles.cell}><Text key={-i} style={styles.timeText}>{i % 12 || 12}:00 {i < 12 ? "AM" : "PM"}</Text></View>);
  }

  let dayTexts = ["M", "T", "W", "Th", "F"].map((day, index) => (
    <View key={index} style={styles.cell}>
      <Text style={styles.dayText}>{day}</Text>
    </View>
  ));

  let grid = []
  for (let k = 0; k < 5; k++) {
    let gridCells = []

    // half a grid cell at the beginning
    gridCells.push(<View key={-(startTime - 1)} style={{ ...styles.gridCellTopHalf }} />);
    for (let i = startTime; i < endTime; i++) {
      let isPresent = exampleSchedule[k] && exampleSchedule[k]![0] <= i && i < exampleSchedule[k]![1];

      gridCells.push(
        <View key={-i} style={isPresent ? styles.gridCellFilled : { flex: 1, }} />
      );
      gridCells.push(
        <View key={i} style={isPresent ? styles.gridCellFilled : styles.gridCellTopHalf} />
      );
    }
    // half a grid cell at the end
    gridCells.push(<View key={(startTime - 1)} style={{ flex: 1 }} />);

    grid.push(<View key={k} style={styles.gridCellInside}>{gridCells}</View>);
  } 

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ flex: 1/12, flexDirection: "row" }}>
        <View style={{ flex: 1 }} />
        {dayTexts}
      </View>
      <View style={ styles.row }>
        <View style={{ flex: 1, justifyContent: "space-between" }}>
            {timeTexts}
        </View>
        {grid}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flex: 1,
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
    fontSize: 11,
    fontWeight: "500",
    textAlign: "right",
  },
  gridCellTopHalf: {
    flex: 1, 
    borderBottomWidth: 1, 
    borderBottomColor: colors.border, 
  },
  gridCellInside: {
    flex: 1, 
    borderRightWidth: 1, 
    borderRightColor: colors.border   
  },
  gridCellFilled: {
    flex: 1, 
    backgroundColor: colors.accent,
    borderColor: colors.accent,
    borderWidth: 1,
  }
});
