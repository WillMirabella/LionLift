import Ionicons from '@expo/vector-icons/Ionicons';
import { View, StyleSheet,Text} from 'react-native';
import { colors } from '../constants/colors';

type Props = {
  step: number;
  steps: number;
};

const Stepper = ({step,steps}: Props) => {
  const elements = [];
  for (let i = 1; i <= steps; i++) {
    if(i<=step) elements.push(<Ionicons key={i} name="ellipse" size={16} color={colors.secondary}></Ionicons>);
    else  elements.push(<Ionicons key={i} name="ellipse-outline" size={16} color={colors.secondary}></Ionicons>);
  }

  return <View style={styles.container}>{elements}</View>;
}

export default Stepper;

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 36,
  },
});