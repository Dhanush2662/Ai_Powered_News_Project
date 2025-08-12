import React from 'react';

interface CountryFilterProps {
  selectedCountry: string;
  onSelect: (countryCode: string) => void;
}

const CountryFilter: React.FC<CountryFilterProps> = ({ selectedCountry, onSelect }) => {
  const countries = [
    { code: 'in', name: '🇮🇳 India' },
    { code: 'us', name: '🇺🇸 USA' },
    { code: 'gb', name: '🇬🇧 UK' },
    { code: 'au', name: '🇦🇺 Australia' },
    { code: 'ca', name: '🇨🇦 Canada' },
    { code: 'de', name: '🇩🇪 Germany' },
    { code: 'fr', name: '🇫🇷 France' },
    { code: 'jp', name: '🇯🇵 Japan' }
  ];

  return (
    <div className="mb-6">
      <label htmlFor="country-select" className="block text-sm font-medium text-gray-700 mb-2">
        Select Country
      </label>
      <select
        id="country-select"
        value={selectedCountry}
        onChange={(e) => onSelect(e.target.value)}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      >
        {countries.map((country) => (
          <option key={country.code} value={country.code}>
            {country.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default CountryFilter;
