import React, { useState } from 'react';
import { LanguageIcon, ArrowsRightLeftIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Translator: React.FC = () => {
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('hi');
  const [loading, setLoading] = useState(false);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ar', name: 'Arabic' }
  ];

  const handleTranslate = async () => {
    if (!sourceText.trim()) {
      toast.error('Please enter text to translate');
      return;
    }

    setLoading(true);
    try {
      // TODO: Implement translation API call
      // const response = await fetchFromAPI('/api/translate', {
      //   method: 'POST',
      //   data: { text: sourceText, source_lang: sourceLang, target_lang: targetLang }
      // });
      
      // Mock translation for now
      setTimeout(() => {
        setTranslatedText(`[Translated from ${sourceLang} to ${targetLang}]: ${sourceText}`);
        setLoading(false);
        toast.success('Translation completed!');
      }, 1500);
    } catch (error) {
      toast.error('Error translating text');
      setLoading(false);
    }
  };

  const swapLanguages = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setSourceText(translatedText);
    setTranslatedText(sourceText);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Multi-language Translator</h1>
        <p className="text-gray-600">Translate news articles and text between different languages</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Source Language */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700">
                From
              </label>
              <select
                value={sourceLang}
                onChange={(e) => setSourceLang(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
            
            <textarea
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
              placeholder="Enter text to translate..."
              className="w-full h-40 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>

          {/* Swap Button */}
          <div className="lg:hidden flex justify-center">
            <button
              onClick={swapLanguages}
              className="p-2 text-gray-500 hover:text-blue-600 transition-colors"
            >
              <ArrowsRightLeftIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Target Language */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700">
                To
              </label>
              <select
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
            
            <textarea
              value={translatedText}
              readOnly
              placeholder="Translation will appear here..."
              className="w-full h-40 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 resize-none"
            />
          </div>
        </div>

        {/* Swap Button for Desktop */}
        <div className="hidden lg:flex justify-center mt-4">
          <button
            onClick={swapLanguages}
            className="p-2 text-gray-500 hover:text-blue-600 transition-colors"
          >
            <ArrowsRightLeftIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="mt-6 flex justify-center">
          <button
            onClick={handleTranslate}
            disabled={loading}
            className="btn-primary flex items-center space-x-2"
          >
            <LanguageIcon className="h-4 w-4" />
            <span>{loading ? 'Translating...' : 'Translate'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Translator;