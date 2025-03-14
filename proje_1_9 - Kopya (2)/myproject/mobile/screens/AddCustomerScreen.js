// mobile/screens/AddCustomerScreen.js
import React, { useState, useEffect, useContext } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  Button, 
  StyleSheet, 
  Alert, 
  ScrollView,
  Platform,
  TouchableOpacity
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import DateTimePicker from '@react-native-community/datetimepicker';
import { AuthContext } from '../context/AuthContext';

export default function AddCustomerScreen({ navigation }) {
  const { user, token } = useContext(AuthContext);  // Giriş yapan temsilci bilgisi ve token

  // Form alanları için state'ler
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [identification, setIdentification] = useState('');
  const [taxOffice, setTaxOffice] = useState('');
  const [address, setAddress] = useState('');
  const [subscriptionType, setSubscriptionType] = useState('');
  const [subscriptionDuration, setSubscriptionDuration] = useState('');
  const [subscriptionStartDate, setSubscriptionStartDate] = useState(new Date());
  const [paymentType, setPaymentType] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [agreementStatus, setAgreementStatus] = useState('');

  // Tarih seçici görünürlüğü için state
  const [showDatePicker, setShowDatePicker] = useState(false);

  // Dinamik olarak API'den çekilecek veriler için state'ler
  const [subscriptionTypes, setSubscriptionTypes] = useState([]);
  const [subscriptionDurations, setSubscriptionDurations] = useState([]);
  const [paymentTypes, setPaymentTypes] = useState([]);
  const [agreementStatuses, setAgreementStatuses] = useState([]);

  // API URL'lerini kendinize göre güncelleyin
  const SERVER_IP = 'http://172.20.10.3:8000';

  useEffect(() => {
    fetchPickerOptions();
  }, [token]); // token güncellendiğinde yeniden denesin

  const fetchPickerOptions = async () => {
    try {
      // Eğer token varsa header ekleyelim:
      const headers = token
        ? { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
        : { 'Content-Type': 'application/json' };

      // Abonelik Türü
      const subTypesResponse = await fetch(`${SERVER_IP}/api/subscription-types/`, { headers });
      if (subTypesResponse.ok) {
        const subTypesData = await subTypesResponse.json();
        setSubscriptionTypes(subTypesData);
      } else {
        console.error('Subscription types fetch failed', subTypesResponse.status);
      }
      
      // Abonelik Süresi
      const subDurationsResponse = await fetch(`${SERVER_IP}/api/subscription-durations/`, { headers });
      if (subDurationsResponse.ok) {
        const subDurationsData = await subDurationsResponse.json();
        setSubscriptionDurations(subDurationsData);
      } else {
        console.error('Subscription durations fetch failed', subDurationsResponse.status);
      }
      
      // Ödeme Türü
      const paymentTypesResponse = await fetch(`${SERVER_IP}/api/payment-types/`, { headers });
      if (paymentTypesResponse.ok) {
        const paymentTypesData = await paymentTypesResponse.json();
        setPaymentTypes(paymentTypesData);
      } else {
        console.error('Payment types fetch failed', paymentTypesResponse.status);
      }
      
      // Anlaşma Durumları: Modelde choices olduğu için sabit tanımlıyoruz
      setAgreementStatuses([
        { id: 'beklemede', name: 'Beklemede' },
        { id: 'olumlu', name: 'Olumlu' },
        { id: 'olumsuz', name: 'Olumsuz' },
      ]);
    } catch (error) {
      console.error('Failed to fetch picker options', error);
    }
  };

  const onChangeDate = (event, selectedDate) => {
    setShowDatePicker(Platform.OS === 'ios'); // iOS'ta picker kalabilir, Android'te kapat.
    if (selectedDate) {
      setSubscriptionStartDate(selectedDate);
    }
  };

  const handleSubmit = async () => {
    // Zorunlu alan kontrolü
    if (
      !username ||
      !firstName ||
      !lastName ||
      !address ||
      !subscriptionStartDate ||
      !amount ||
      !subscriptionType ||
      !subscriptionDuration ||
      !paymentType ||
      !agreementStatus
    ) {
      Alert.alert('Hata', 'Lütfen tüm zorunlu alanları doldurun.');
      return;
    }
    if (!user) {
      Alert.alert('Hata', 'Lütfen önce giriş yapınız.');
      return;
    }

    const newCustomer = {
      username,
      first_name: firstName,
      last_name: lastName,
      identification,
      tax_office: taxOffice,
      address,
      subscription_type: subscriptionType,
      subscription_duration: subscriptionDuration,
      // Tarihi ISO formatında (YYYY-MM-DD) gönderiyoruz
      subscription_start_date: subscriptionStartDate.toISOString().split('T')[0],
      payment_type: paymentType,
      amount: parseFloat(amount),
      description,
      agreement_status: agreementStatus,
      rep: user.id
    };

    try {
      const response = await fetch(`${SERVER_IP}/api/customers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(newCustomer)
      });

      if (response.ok) {
        Alert.alert('Başarılı', 'Müşteri başarıyla eklendi!');
        navigation.navigate('Customers');
      } else {
        Alert.alert('Hata', 'Müşteri eklenemedi. Status: ' + response.status);
      }
    } catch (error) {
      console.error('Hata:', error);
      Alert.alert('Hata', 'Müşteri eklenirken bir hata oluştu.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.pageHeader}>Müşteri Ekle</Text>
      <View style={styles.card}>
        <Text style={styles.cardHeader}>Müşteri Bilgileri</Text>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Kullanıcı Adı</Text>
          <TextInput 
            style={styles.input}
            value={username}
            onChangeText={setUsername}
            placeholder="Kullanıcı adı girin"
          />
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Ad</Text>
          <TextInput 
            style={styles.input}
            value={firstName}
            onChangeText={setFirstName}
            placeholder="Ad girin"
          />
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Soyad</Text>
          <TextInput 
            style={styles.input}
            value={lastName}
            onChangeText={setLastName}
            placeholder="Soyad girin"
          />
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>TC/Vergi No</Text>
          <TextInput 
            style={styles.input}
            value={identification}
            onChangeText={setIdentification}
            placeholder="TC/Vergi No girin"
          />
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Vergi Dairesi</Text>
          <TextInput 
            style={styles.input}
            value={taxOffice}
            onChangeText={setTaxOffice}
            placeholder="Vergi Dairesi girin"
          />
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Adres</Text>
          <TextInput 
            style={[styles.input, { height: 80 }]}
            value={address}
            onChangeText={setAddress}
            placeholder="Adres girin"
            multiline
          />
        </View>
        
        {/* Picker: Abonelik Türü */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Abonelik Türü</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={subscriptionType}
              onValueChange={(itemValue) => setSubscriptionType(itemValue)}
            >
              <Picker.Item label="Seçiniz..." value="" />
              {subscriptionTypes.map((type) => (
                <Picker.Item key={String(type.id)} label={type.name} value={String(type.id)} />
              ))}
            </Picker>
          </View>
        </View>
        
        {/* Picker: Abonelik Süresi */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Abonelik Süresi</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={subscriptionDuration}
              onValueChange={(itemValue) => setSubscriptionDuration(itemValue)}
            >
              <Picker.Item label="Seçiniz..." value="" />
              {subscriptionDurations.map((duration) => (
                <Picker.Item key={String(duration.id)} label={duration.name} value={String(duration.id)} />
              ))}
            </Picker>
          </View>
        </View>
        
        {/* Tarih Seçici: Abonelik Başlangıç Tarihi */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Abonelik Başlangıç Tarihi</Text>
          <TouchableOpacity onPress={() => setShowDatePicker(true)} style={styles.dateButton}>
            <Text style={styles.dateText}>
              {subscriptionStartDate ? subscriptionStartDate.toISOString().split('T')[0] : 'Tarih seçin'}
            </Text>
          </TouchableOpacity>
          {showDatePicker && (
            <DateTimePicker
              value={subscriptionStartDate || new Date()}
              mode="date"
              display="default"
              onChange={onChangeDate}
            />
          )}
        </View>
        
        {/* Picker: Ödeme Türü */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Ödeme Türü</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={paymentType}
              onValueChange={(itemValue) => setPaymentType(itemValue)}
            >
              <Picker.Item label="Seçiniz..." value="" />
              {paymentTypes.map((payment) => (
                <Picker.Item key={String(payment.id)} label={payment.name} value={String(payment.id)} />
              ))}
            </Picker>
          </View>
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Tutar</Text>
          <TextInput 
            style={styles.input}
            value={amount}
            onChangeText={setAmount}
            placeholder="Tutar girin"
            keyboardType="numeric"
          />
        </View>
        
        <View style={styles.formGroup}>
          <Text style={styles.label}>Açıklama</Text>
          <TextInput 
            style={[styles.input, { height: 80 }]}
            value={description}
            onChangeText={setDescription}
            placeholder="Açıklama girin"
            multiline
          />
        </View>
        
        {/* Picker: Anlaşma Durumu */}
        <View style={styles.formGroup}>
          <Text style={styles.label}>Anlaşma Durumu</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={agreementStatus}
              onValueChange={(itemValue) => setAgreementStatus(itemValue)}
            >
              <Picker.Item label="Seçiniz..." value="" />
              {agreementStatuses.map((status) => (
                <Picker.Item key={String(status.id)} label={status.name} value={String(status.id)} />
              ))}
            </Picker>
          </View>
        </View>
        
        <View style={styles.buttonContainer}>
          <Button title="Müşteriyi Kaydet" onPress={handleSubmit} color="#6200ee" />
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#f2f2f2',
  },
  pageHeader: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  cardHeader: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    borderBottomWidth: 1,
    borderColor: '#ddd',
    paddingBottom: 8,
  },
  formGroup: {
    marginBottom: 12,
  },
  label: {
    marginBottom: 5,
    fontWeight: '600',
    color: '#333',
  },
  input: {
    backgroundColor: '#fff',
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#ccc',
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    backgroundColor: '#fff',
  },
  dateButton: {
    backgroundColor: '#fff',
    paddingHorizontal: 10,
    paddingVertical: 12,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#ccc',
    justifyContent: 'center',
  },
  dateText: {
    color: '#333',
  },
  buttonContainer: {
    marginTop: 20,
  },
});
