import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useTransactions } from '../context/TransactionContext';
import TransactionList from '../components/transactions/TransactionList';
import TransactionForm from '../components/transactions/TransactionForm';
import Modal from '../components/common/Modal';
import type { Transaction } from '../types';

export default function Transactions() {
  const { transactions, addTransaction, updateTransaction, deleteTransaction } = useTransactions();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | undefined>();

  const handleOpenModal = (transaction?: Transaction) => {
    setEditingTransaction(transaction);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setEditingTransaction(undefined);
    setIsModalOpen(false);
  };

  const handleSubmit = (data: Omit<Transaction, 'id' | 'recurring'>) => {
    if (editingTransaction) {
      updateTransaction(editingTransaction.id, { ...data, recurring: false });
    } else {
      addTransaction({ ...data, recurring: false });
    }
    handleCloseModal();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Transactions</h1>
          <p className="text-gray-500 dark:text-gray-400">Manage your income and expenses.</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2 font-medium text-white shadow-sm hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
        >
          <Plus className="h-5 w-5" />
          Add Transaction
        </button>
      </div>

      <TransactionList 
        transactions={transactions} 
        onEdit={handleOpenModal} 
        onDelete={deleteTransaction} 
      />

      <Modal 
        isOpen={isModalOpen} 
        onClose={handleCloseModal} 
        title={editingTransaction ? 'Edit Transaction' : 'Add New Transaction'}
      >
        <TransactionForm 
          initialData={editingTransaction} 
          onSubmit={handleSubmit} 
          onCancel={handleCloseModal} 
        />
      </Modal>
    </div>
  );
}
