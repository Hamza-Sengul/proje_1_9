import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator, Image, SafeAreaView, StatusBar } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons'; // Expo kullanıyorsanız

export default function CustomersScreen() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      // Django server IP'ni burada ayarla (localhost çalışmayabilir)
      const response = await fetch('http://172.20.10.3:8000/api/customers/');
      if (!response.ok) {
        throw new Error('Sunucu yanıt vermedi');
      }
      const data = await response.json();
      setCustomers(data);
      setError(null);
    } catch (error) {
      console.error('Hata:', error);
      setError('Müşteriler yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.customerCard}
      onPress={() => console.log('Müşteri seçildi:', item.id)}
    >
      <View style={styles.customerInfo}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>
            {item.first_name.charAt(0)}{item.last_name.charAt(0)}
          </Text>
        </View>
        <View style={styles.textContainer}>
          <Text style={styles.customerName}>{item.first_name} {item.last_name}</Text>
          <Text style={styles.customerAddress}>{item.address}</Text>
          {item.subscription_start_date && (
            <Text style={styles.subscriptionDate}>
              Abonelik: {new Date(item.subscription_start_date).toLocaleDateString('tr-TR')}
            </Text>
          )}
        </View>
      </View>
      <View style={styles.statusContainer}>
        <Text style={[
          styles.statusText, 
          item.agreement_status === 'onaylandı' ? styles.statusApproved : 
          item.agreement_status === 'reddedildi' ? styles.statusRejected : 
          styles.statusPending
        ]}>
          {item.agreement_status || 'beklemede'}
        </Text>
        <MaterialIcons name="chevron-right" size={24} color="#999" />
      </View>
    </TouchableOpacity>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>Müşteri Listesi</Text>
      <TouchableOpacity 
        style={styles.addButton}
        onPress={() => console.log('Yeni müşteri ekle')}
      >
        <MaterialIcons name="add" size={24} color="white" />
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      {renderHeader()}
      
      {loading ? (
        <View style={styles.loaderContainer}>
          <ActivityIndicator size="large" color="#0066cc" />
          <Text style={styles.loaderText}>Müşteriler yükleniyor...</Text>
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <MaterialIcons name="error-outline" size={48} color="#ff6b6b" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={fetchCustomers}>
            <Text style={styles.retryButtonText}>Tekrar Dene</Text>
          </TouchableOpacity>
        </View>
      ) : customers.length === 0 ? (
        <View style={styles.emptyContainer}>
          <MaterialIcons name="people-outline" size={48} color="#999" />
          <Text style={styles.emptyText}>Henüz müşteri eklenmemiş</Text>
          <TouchableOpacity style={styles.addNewButton} onPress={() => console.log('Yeni müşteri ekle')}>
            <Text style={styles.addNewButtonText}>Yeni Müşteri Ekle</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={customers}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          refreshing={loading}
          onRefresh={fetchCustomers}
        />
      )}
    </SafeAreaView>
  );
}

// Müşteri ekleme fonksiyonu (gerekirse bunu bir button'a bağlayabilirsiniz)
const createCustomer = async (newCustomer) => {
  try {
    const response = await fetch('http://172.20.10.3:8000/api/customers/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newCustomer)
    });
    if (response.ok) {
      console.log('Başarıyla eklendi!');
      return true;
    } else {
      console.log('Eklenemedi, status:', response.status);
      return false;
    }
  } catch (error) {
    console.error('Hata:', error);
    return false;
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#0066cc',
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    padding: 16,
  },
  customerCard: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  customerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  avatarContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#0066cc',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  textContainer: {
    flex: 1,
  },
  customerName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  customerAddress: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  subscriptionDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: 8,
  },
  statusApproved: {
    backgroundColor: '#e6f7ed',
    color: '#2e7d32',
  },
  statusRejected: {
    backgroundColor: '#ffebee',
    color: '#c62828',
  },
  statusPending: {
    backgroundColor: '#fff8e1',
    color: '#ff8f00',
  },
  separator: {
    height: 12,
  },
  loaderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loaderText: {
    marginTop: 8,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  errorText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  retryButton: {
    marginTop: 16,
    backgroundColor: '#0066cc',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
  },
  retryButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
  },
  addNewButton: {
    marginTop: 16,
    backgroundColor: '#0066cc',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
  },
  addNewButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});