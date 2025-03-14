import 'react-native-gesture-handler';
import React, { useContext } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { AuthProvider, AuthContext } from './context/AuthContext';
import LoginScreen from './screens/LoginScreen';
import HomeScreen from './screens/HomeScreen';
import CustomersScreen from './screens/CustomersScreen';
import AddCustomerScreen from './screens/AddCustomerScreen';

const Drawer = createDrawerNavigator();

function AppNavigator() {
  const { user } = useContext(AuthContext);

  // Eğer user null ise, kullanıcı henüz giriş yapmamış demektir.
  if (!user) {
    return (
      <Drawer.Navigator screenOptions={{ headerShown: false }}>
        <Drawer.Screen name="Login" component={LoginScreen} />
      </Drawer.Navigator>
    );
  }

  return (
    <Drawer.Navigator>
      <Drawer.Screen name="Home" component={HomeScreen} />
      <Drawer.Screen name="Customers" component={CustomersScreen} />
      <Drawer.Screen name="AddCustomer" component={AddCustomerScreen} options={{ title: 'Müşteri Ekle' }} />

    </Drawer.Navigator>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
}
