'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiArrowLeft } from 'react-icons/fi';

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800 py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full space-y-8"
      >
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Reset your password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-400">
            This feature is coming soon
          </p>
        </div>

        <div className="bg-gray-800 p-8 rounded-lg shadow-2xl space-y-6">
          <p className="text-gray-300 text-center">
            Password reset functionality will be available in a future update.
          </p>
          
          <Link
            href="/login"
            className="flex items-center justify-center space-x-2 text-blue-400 hover:text-blue-300"
          >
            <FiArrowLeft />
            <span>Back to login</span>
          </Link>
        </div>

        <div className="text-center text-xs text-gray-500">
          <p>Built by Nikhil Dodda</p>
        </div>
      </motion.div>
    </div>
  );
}
