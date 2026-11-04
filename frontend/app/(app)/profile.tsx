
import { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/colors";

export default function ProfileScreen() {
  // Placeholder user information
  const [user, setUser] = useState({
    id: 1,
    first_name: "",
    last_name: "",
    phone: "",
    email: "abc123@psu.edu",
    gender: "",
    description: "PSU Student",
    grad_year: "",
    major: "",
    address: "",
    preferred_payment: "",
    car_id: null as number | null,
  });

  // Edit profile state
  const [isEditing, setIsEditing] = useState(false);
  const [draftUser, setDraftUser] = useState({ ...user });

  // Start editing
  const startEditing = () => {
    setDraftUser({ ...user });
    setIsEditing(true);
  };

  // Save changes
  const saveChanges = () => {
    setUser({ ...draftUser });
    setIsEditing(false);
  };

  // Cancel changes
  const cancelEditing = () => {
    setDraftUser({ ...user });
    setIsEditing(false);
  };

  // Placeholder vehicle information
  const car = {
    id: null,
    make: "Not provided",
    model: "Not provided",
    color: "Not provided",
    year: "Not provided",
    capacity: "Not provided",
  };

  // Placeholder weekly schedule
  const schedule = [
    ["Monday", "11 AM - 3 PM"],
    ["Tuesday", "10 AM - 2 PM"],
    ["Wednesday", "11 AM - 3 PM"],
    ["Thursday", "10 AM - 2 PM"],
    ["Friday", "11 AM - 1 PM"],
  ];

  // Editable personal information fields
  const editableFields = [
    ["First Name", "first_name"],
    ["Last Name", "last_name"],
    ["Phone", "phone"],
    ["Email", "email"],
    ["Gender", "gender"],
    ["Graduation Year", "grad_year"],
    ["Major", "major"],
    ["Description", "description"],
    ["Address", "address"],
    ["Preferred Payment", "preferred_payment"],
  ] as const;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        {/* Profile Header */}
        <View style={styles.profileHeader}>
          <View style={styles.avatarCircle}>
            <Ionicons
              name="person"
              size={60}
              color="#FFFFFF"
            />
          </View>

          {/* Edit / Save Button */}
          <TouchableOpacity
            style={styles.editButton}
            onPress={isEditing ? saveChanges : startEditing}
          >
            <Ionicons
              name={isEditing ? "checkmark" : "pencil"}
              size={16}
              color={colors.primary}
            />
            <Text style={styles.editButtonText}>
              {isEditing ? "Save Changes" : "Edit Profile"}
            </Text>
          </TouchableOpacity>

          {/* Cancel Button */}
          {isEditing && (
            <TouchableOpacity onPress={cancelEditing}>
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Personal Information */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>
            Personal Information
          </Text>

          <View style={styles.infoGrid}>
            <InfoItem label="User ID" value={user.id} />

            {editableFields.map(([label, key]) => (
              <View key={key} style={styles.infoItem}>
                <Text style={styles.label}>{label}</Text>

                {isEditing ? (
                  <TextInput
                    style={styles.textInput}
                    value={draftUser[key]}
                    onChangeText={(text) =>
                      setDraftUser((previous) => ({
                        ...previous,
                        [key]: text,
                      }))
                    }
                    placeholder="Enter information"
                    placeholderTextColor="#999999"
                  />
                ) : (
                  <Text style={styles.value}>
                    {user[key] || "Not provided"}
                  </Text>
                )}
              </View>
            ))}

            <InfoItem label="Car ID" value={user.car_id} />
          </View>
        </View>

        {/* Vehicle Information */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>
            Vehicle Information
          </Text>

          <View style={styles.infoGrid}>
            <InfoItem label="Car ID" value={car.id} />
            <InfoItem label="Make" value={car.make} />
            <InfoItem label="Model" value={car.model} />
            <InfoItem label="Color" value={car.color} />
            <InfoItem label="Year" value={car.year} />
            <InfoItem label="Capacity" value={car.capacity} />
          </View>
        </View>

        {/* Weekly Schedule */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>
            Weekly Schedule
          </Text>

          {schedule.map(([day, time]) => (
            <View key={day} style={styles.scheduleRow}>
              <Text style={styles.day}>{day}</Text>
              <Text style={styles.time}>{time}</Text>
            </View>
          ))}
        </View>

        {/* Estimated Route */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>
            Estimated Route
          </Text>

          <View style={styles.mapPlaceholder}>
            <Ionicons
              name="map-outline"
              size={40}
              color={colors.primary}
            />

            <Text style={styles.mapTitle}>
              Map Placeholder
            </Text>

            <Text style={styles.mapDescription}>
              Estimated route will appear here
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// Reusable component for information fields
function InfoItem({
  label,
  value,
}: {
  label: string;
  value: string | number | null;
}) {
  return (
    <View style={styles.infoItem}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>
        {value ?? "Not provided"}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },

  content: {
    padding: 20,
    paddingBottom: 40,
    width: "100%",
    maxWidth: 900,
    alignSelf: "center",
  },

  profileHeader: {
    alignItems: "center",
    marginBottom: 25,
    marginTop: 10,
  },

  avatarCircle: {
    width: 110,
    height: 110,
    borderRadius: 55,
    backgroundColor: "#D3D3D3",
    justifyContent: "center",
    alignItems: "center",
  },

  editButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.accent,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    marginTop: 15,
    gap: 8,
  },

  editButtonText: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: "600",
  },

  cancelText: {
    color: colors.secondary,
    fontSize: 14,
    marginTop: 12,
  },

  card: {
    backgroundColor: "#FFFFFF",
    padding: 20,
    borderRadius: 15,
    marginBottom: 18,
    borderWidth: 1,
    borderColor: "#EEEEEE",

    shadowColor: "#000000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 5,
    elevation: 3,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: colors.primary,
    marginBottom: 18,
  },

  infoGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
  },

  infoItem: {
    width: "48%",
    marginBottom: 12,
  },

  label: {
    fontSize: 15,
    color: "#777777",
    marginBottom: 5,
  },

  value: {
    fontSize: 15,
    color: colors.primary,
    fontWeight: "500",
  },

  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 15,
    color: colors.primary,
    backgroundColor: "#FFFFFF",
    width: "100%",
  },

  scheduleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#EEEEEE",
  },

  day: {
    fontSize: 15,
    color: colors.primary,
    fontWeight: "500",
  },

  time: {
    fontSize: 15,
    color: colors.secondary,
  },

  mapPlaceholder: {
    height: 280,
    backgroundColor: "#D3D3D3",
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
    padding: 15,
  },

  mapTitle: {
    fontSize: 17,
    fontWeight: "bold",
    color: colors.primary,
    marginTop: 10,
  },

  mapDescription: {
    fontSize: 12,
    color: colors.secondary,
    marginTop: 5,
    textAlign: "center",
  },
});
