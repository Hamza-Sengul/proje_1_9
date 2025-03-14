// mobile/screens/LoginScreen.js
import React, { useState, useContext } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { CommonActions } from '@react-navigation/native';
import { AuthContext } from '../context/AuthContext';

export default function LoginScreen({ navigation }) {
  const { setUser, setToken } = useContext(AuthContext);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const SERVER_IP = 'http://172.20.10.3:8000';

  const handleLogin = async () => {
    try {
      const tokenResponse = await fetch(`${SERVER_IP}/api/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!tokenResponse.ok) {
        Alert.alert('Giriş Hatası', 'Kullanıcı adı veya şifre hatalı.');
        return;
      }

      const tokenData = await tokenResponse.json();
      setToken(tokenData.access);

      const userResponse = await fetch(`${SERVER_IP}/api/users/me/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokenData.access}`,
        },
      });

      if (!userResponse.ok) {
        Alert.alert('Hata', 'Kullanıcı bilgileri alınamadı.');
        return;
      }

      const userData = await userResponse.json();
      setUser(userData);

      // Reset navigasyonu, navigator tamamen mount olduktan sonra çalışsın.
      setTimeout(() => {
        navigation.dispatch(
          CommonActions.reset({
            index: 0,
            routes: [{ name: 'Home' }],
          })
        );
      }, 0);

    } catch (error) {
      console.error(error);
      Alert.alert('Hata', 'Giriş yapılırken bir hata oluştu.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Temsilci Giriş</Text>
      <TextInput
        style={styles.input}
        placeholder="Kullanıcı Adı"
        value={username}
        onChangeText={setUsername}
      />
      <TextInput
        style={styles.input}
        placeholder="Şifre"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Giriş Yap" onPress={handleLogin} color="#6200ee" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    padding: 10,
    marginBottom: 15,
    backgroundColor: '#fff',
  },
});
