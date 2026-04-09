import React, { useState, useEffect } from 'react'
import { useMutation } from 'react-query'
import { createJob, generateJD } from '../services/api'
import { Plus, Trash2, Sparkles, ChevronDown, X } from 'lucide-react'
import { JOB_CATEGORIES, SUB_CATEGORY_TEMPLATES, CATEGORY_DEFAULTS } from '../data/jobTemplates'
import { useNotify } from '../contexts/NotifyContext'
import '../styles/JobPosting.css'

const CATEGORY_GROUPS = {
  standard: [
    { id: 'core', label: 'Core Competencies', placeholder: 'e.g., Analytical Skills, Decision Making' },
    { id: 'technical', label: 'Technical Skills', placeholder: 'e.g., Python, Salesforce, Adobe Suite' },
    { id: 'soft', label: 'Soft Skills', placeholder: 'e.g., Communication, Leadership' },
    { id: 'professional', label: 'Professional Skills', placeholder: 'e.g., Project Management, Agile' },
    { id: 'tools', label: 'Tools & Technologies', placeholder: 'e.g., Slack, Jira, Docker' },
    { id: 'languages', label: 'Languages', placeholder: 'e.g., English, Spanish' }
  ],
  industry: [
    { id: 'analytics', label: 'Analytics', placeholder: 'e.g., SQL, A/B Testing' },
    { id: 'design', label: 'Visual Design', placeholder: 'e.g., Figma, Photoshop' },
    { id: 'project', label: 'Project Management', placeholder: 'e.g., Risk Management, Budgeting' },
    { id: 'marketing', label: 'Digital Marketing', placeholder: 'e.g., SEO/SEM, Google Analytics' }
  ]
}

function JobPosting() {
  const { success, error: notifyError, warning } = useNotify()
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    description: '',
    location: '',
    job_type: 'full-time',
    experience_required: '',
    salary_min: '',
    salary_max: ''
  })

  // Hierarchical selection state (Category -> Sub-category only)
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedSubCategory, setSelectedSubCategory] = useState('')
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  // Categorized skills state: Handles custom text input for each category
  const [skillsByCategory, setSkillsByCategory] = useState({
    core: '', technical: '', soft: '', professional: '', tools: '', languages: '',
    analytics: '', design: '', project: '', marketing: '', experience: '', education: ''
  })

  // Track checked items specifically for the new checklist UI
  const [checkedItems, setCheckedItems] = useState({})

  // Dynamic Categories added by user
  const [dynamicCategories, setDynamicCategories] = useState([])
  const [newCategoryName, setNewCategoryName] = useState('')
  const [showAddCategory, setShowAddCategory] = useState(false)

  // -- NEW: Custom Category & Sub-category states --
  const [customMainCategories, setCustomMainCategories] = useState([])
  const [customSubCategories, setCustomSubCategories] = useState({}) // { mainCatId: [subCatName, ...] }
  const [showAddMainInput, setShowAddMainInput] = useState(false)
  const [showAddSubInput, setShowAddSubInput] = useState(false)
  const [newMainName, setNewMainName] = useState('')
  const [newSubName, setNewSubName] = useState('')

  const handleAddCustomMain = () => {
    if (!newMainName.trim()) return;
    if (JOB_CATEGORIES[newMainName] || customMainCategories.includes(newMainName)) {
      warning("This category already exists.");
      return;
    }
    setCustomMainCategories([...customMainCategories, newMainName]);
    setSelectedCategory(newMainName);
    setSelectedSubCategory('');
    setNewMainName('');
    setShowAddMainInput(false);
  }

  const handleAddCustomSub = () => {
    if (!newSubName.trim()) return;
    const currentSubs = [
      ...(JOB_CATEGORIES[selectedCategory] || []),
      ...(customSubCategories[selectedCategory] || [])
    ];
    if (currentSubs.includes(newSubName)) {
      warning("This sub-category already exists.");
      return;
    }
    setCustomSubCategories(prev => ({
      ...prev,
      [selectedCategory]: [...(prev[selectedCategory] || []), newSubName]
    }));
    setSelectedSubCategory(newSubName);
    setNewSubName('');
    setShowAddSubInput(false);
  }

  // Handle template population from Sub-category OR Category Default
  useEffect(() => {
    const activeTemplate = selectedSubCategory && SUB_CATEGORY_TEMPLATES[selectedSubCategory];
    const categoryDefault = selectedCategory && CATEGORY_DEFAULTS[selectedCategory];
    const systemDefault = CATEGORY_DEFAULTS.Default;

    const dataSource = activeTemplate || categoryDefault || (selectedCategory ? systemDefault : null);

    if (dataSource) {
      setFormData(prev => ({
        ...prev,
        title: selectedSubCategory || selectedCategory || prev.title || '',
        description: dataSource.description || prev.description,
        experience_required: dataSource.experience_required || prev.experience_required
      }));

      // Set default checked items from the template/baseline
      const newChecked = {};
      if (dataSource.checklists) {
        Object.entries(dataSource.checklists).forEach(([catId, items]) => {
          items.forEach(item => {
            newChecked[`${catId}-${item}`] = true;
          });
        });
      }
      setCheckedItems(newChecked);

      // Clear custom skills on template change
      setSkillsByCategory({
        core: '', technical: '', soft: '', professional: '', tools: '', languages: '',
        analytics: '', design: '', project: '', marketing: '', experience: '', education: ''
      });
    }
  }, [selectedSubCategory, selectedCategory]);

  const createJobMutation = useMutation(createJob, {
    onSuccess: () => {
      success('Job posted successfully! 🎉')
      setFormData({
        title: '', company: '', description: '', location: '',
        job_type: 'full-time', experience_required: '', salary_min: '', salary_max: ''
      })
      setSkillsByCategory({
        core: '', technical: '', soft: '', professional: '', tools: '', languages: '',
        analytics: '', design: '', project: '', marketing: ''
      })
      setSelectedCategory('')
      setSelectedSubCategory('')
    },
    onError: (error) => {
      notifyError('Failed to post job: ' + (error.response?.data?.detail || error.message))
    }
  })

  const [isGeneratingJD, setIsGeneratingJD] = useState(false)

  const generateJDMutation = useMutation(
    (data) => generateJD(data),
    {
      onSuccess: (response) => {
        setFormData(prev => ({ ...prev, description: response.data.job_description }))
        setIsGeneratingJD(false)
      },
      onError: (err) => {
        notifyError("AI JD Generation failed. Please try again.")
        setIsGeneratingJD(false)
      }
    }
  )

  const handleGenerateAIJD = () => {
    if (!formData.title) {
      warning("Please enter a Job Title first.")
      return
    }

    // Collect all skills as key points
    const points = Object.values(skillsByCategory).filter(v => v.trim()).join(', ')

    setIsGeneratingJD(true)
    generateJDMutation.mutate({
      title: formData.title,
      key_points: points || "Dynamic role requiring expertise in several areas."
    })
  }

  const toggleCheckItem = (catId, item) => {
    const key = `${catId}-${item}`;
    setCheckedItems(prev => ({ ...prev, [key]: !prev[key] }));
  }

  const handleCustomSkillChange = (catId, value) => {
    setSkillsByCategory(prev => ({ ...prev, [catId]: value }));
  }

  const handleAddCategory = () => {
    if (!newCategoryName.trim()) return
    const id = newCategoryName.toLowerCase().replace(/\s+/g, '_')
    if (dynamicCategories.find(c => c.id === id)) {
      warning("This category already exists.")
      return
    }
    setDynamicCategories([...dynamicCategories, { id, label: newCategoryName }])
    setNewCategoryName('')
    setShowAddCategory(false)
  }

  const removeDynamicCategory = (id) => {
    setDynamicCategories(dynamicCategories.filter(c => c.id !== id))
    // Also clear its skills
    setSkillsByCategory(prev => {
      const { [id]: removed, ...rest } = prev
      return rest
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const processedCategories = {}
    const allSkillsList = []

    // 1. Process checked items
    Object.entries(checkedItems).forEach(([key, isChecked]) => {
      if (isChecked) {
        const [catId, ...itemParts] = key.split('-');
        const item = itemParts.join('-');
        if (!processedCategories[catId]) processedCategories[catId] = [];
        processedCategories[catId].push(item);
        allSkillsList.push(item);
      }
    });

    // 2. Process custom skills (text inputs)
    Object.entries(skillsByCategory).forEach(([catId, value]) => {
      if (value.trim()) {
        const customArr = value.split(',').map(s => s.trim()).filter(s => s)
        if (!processedCategories[catId]) processedCategories[catId] = [];
        processedCategories[catId].push(...customArr);
        allSkillsList.push(...customArr);
      }
    })

    const jobData = {
      ...formData,
      required_skills: [...new Set(allSkillsList)],
      skills_by_category: processedCategories,
      experience_required: formData.experience_required ? parseFloat(formData.experience_required) : null,
      salary_min: formData.salary_min ? parseFloat(formData.salary_min) : null,
      salary_max: formData.salary_max ? parseFloat(formData.salary_max) : null
    }

    createJobMutation.mutate(jobData)
  }

  // Helper to render a requirement group
  const renderRequirementGroup = (id, label, items = [], isDynamic = false) => {
    if (!isDynamic && (!items || items.length === 0)) return null;
    return (
      <div className={`skill-category-group ${isDynamic ? 'dynamic-group' : ''}`} key={id}>
        <div className="group-header">
          <h4>{label}</h4>
          {isDynamic && (
            <button
              type="button"
              className="btn-remove-cat"
              onClick={() => removeDynamicCategory(id)}
              title="Remove Category"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>

        {items.length > 0 && (
          <div className="checklist-container">
            {items.map(item => (
              <label key={item} className="checklist-item">
                <input
                  type="checkbox"
                  checked={!!checkedItems[`${id}-${item}`]}
                  onChange={() => toggleCheckItem(id, item)}
                />
                <span className="checkbox-custom"></span>
                {item}
              </label>
            ))}
          </div>
        )}

        <div className="custom-input-wrapper">
          <input
            type="text"
            className="custom-skill-input"
            value={skillsByCategory[id] || ''}
            onChange={(e) => handleCustomSkillChange(id, e.target.value)}
            placeholder={isDynamic ? `List ${label} (comma separated)...` : `+ Add Custom ${label}...`}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="job-posting page-container">
      <div className="posting-header">
        <h1>🚀 Post a New Opportunity</h1>
        <p>Choose a category for faster recruiting with pre-defined requirements.</p>
      </div>

      <form onSubmit={handleSubmit} className="job-form">
        <div className="form-section template-selection">
          <h3 className="section-title">📂 Job Category</h3>
          <p className="section-subtitle">Select an industry suite to reveal specialized fields and professional requirements.</p>

          <div className="selection-flow">
            {/* Main Category Custom Dropdown */}
            <div className="custom-dropdown-container">
              <label className="dropdown-label">Industry Suite</label>
              <div className={`custom-select-wrapper ${isDropdownOpen ? 'open' : ''}`}>
                <div
                  className="select-trigger"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                >
                  <div className="trigger-text">
                    {selectedCategory || '-- Click to select an industry suite --'}
                  </div>
                  <ChevronDown className={`chevron ${isDropdownOpen ? 'rotate' : ''}`} size={18} />
                </div>

                {isDropdownOpen && (
                  <div className="select-options-drawer">
                    {[...Object.keys(JOB_CATEGORIES), ...customMainCategories].map(cat => (
                      <div
                        key={cat}
                        className={`option-item ${selectedCategory === cat ? 'active' : ''}`}
                        onClick={() => {
                          setSelectedCategory(cat);
                          setSelectedSubCategory('');
                          setIsDropdownOpen(false);
                        }}
                      >
                        {cat}
                      </div>
                    ))}
                    <div
                      className="option-item add-new-option"
                      onClick={() => {
                        setSelectedCategory('ADD_NEW');
                        setIsDropdownOpen(false);
                      }}
                    >
                      <Plus size={14} />
                      <span>Add Custom Suite</span>
                    </div>
                  </div>
                )}

                {/* Inline Add for Main Category */}
                {selectedCategory === 'ADD_NEW' && (
                  <div className="inline-add-overlay">
                    <div className="inline-add-form">
                      <input
                        type="text"
                        value={newMainName}
                        onChange={(e) => setNewMainName(e.target.value)}
                        placeholder="Enter Suite Name..."
                        autoFocus
                        onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomMain())}
                      />
                      <div className="inline-actions">
                        <button type="button" onClick={handleAddCustomMain} className="btn-icon-confirm">
                          <Plus size={18} />
                          <span>Add Suite</span>
                        </button>
                        <button type="button" onClick={() => setSelectedCategory('')} className="btn-icon-cancel">
                          <X size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Sub Category List - "downside" (Below) */}
            {selectedCategory && selectedCategory !== 'ADD_NEW' && (
              <div className="sub-category-downside">
                <label className="dropdown-label">Specialized Field (Sub-category)</label>
                <div className="sub-selection-grid">
                  {[...(JOB_CATEGORIES[selectedCategory] || []), ...(customSubCategories[selectedCategory] || [])].map(sub => (
                    <div
                      key={sub}
                      className={`sub-selection-card ${selectedSubCategory === sub ? 'active' : ''}`}
                      onClick={() => setSelectedSubCategory(sub)}
                    >
                      <Sparkles size={14} className="sparkle-icon" />
                      <span>{sub}</span>
                    </div>
                  ))}

                  {/* Add Sub Category Inline Card */}
                  <div className={`sub-selection-card add-card ${showAddSubInput ? 'expanding' : ''}`}>
                    {showAddSubInput ? (
                      <div className="inline-add-form-mini">
                        <input
                          type="text"
                          value={newSubName}
                          onChange={(e) => setNewSubName(e.target.value)}
                          placeholder="Field Name"
                          autoFocus
                          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomSub())}
                        />
                        <div className="mini-actions">
                          <button type="button" onClick={handleAddCustomSub} className="btn-mini-add">
                            <Plus size={14} />
                            <span>Add Field</span>
                          </button>
                          <button type="button" onClick={() => setShowAddSubInput(false)} className="btn-mini-close">
                            <X size={14} />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="add-content" onClick={() => setShowAddSubInput(true)}>
                        <Plus size={18} />
                        <span>Add New Field</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {selectedSubCategory && (
            <div className="selection-summary-badge">
              <Sparkles size={16} />
              <span>Applied Template: <strong>{selectedSubCategory}</strong></span>
            </div>
          )}
        </div>

        <div className="reveal-content-group">
          <div className="form-section">
            <h3 className="section-title">📄 Basic Information</h3>
            <div className="form-group">
              <label>Job Title *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                placeholder="e.g., Senior AI Engineer"
              />
            </div>
            {/* ... rest of the basic info fields ... */}
            <div className="form-group">
              <label>Company *</label>
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                required
                placeholder="Your company name"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="San Francisco or Remote"
                />
              </div>
              <div className="form-group">
                <label>Job Type</label>
                <select
                  value={formData.job_type}
                  onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                >
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <div className="label-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <label>Job Description *</label>
                <button
                  type="button"
                  className="btn-ai-magic"
                  onClick={handleGenerateAIJD}
                  disabled={isGeneratingJD}
                >
                  {isGeneratingJD ? '✨ AI Working...' : '✨ Draft with AI'}
                </button>
              </div>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows="8"
                required
                placeholder="Detail the role and expectations..."
              ></textarea>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Exp. Required (Years)</label>
                <input
                  type="number"
                  value={formData.experience_required}
                  onChange={(e) => setFormData({ ...formData, experience_required: e.target.value })}
                  min="0"
                  placeholder="0"
                />
              </div>
              <div className="form-group">
                <label>Salary Max (₹)</label>
                <input
                  type="number"
                  value={formData.salary_max}
                  onChange={(e) => setFormData({ ...formData, salary_max: e.target.value })}
                  placeholder="Max Salary"
                />
              </div>
            </div>
          </div>

          <div className="form-section skills-matrix structured-checklist">
            <h3 className="section-title">🎯 Targeted Requirements</h3>
            <p className="helper-text">
              {selectedSubCategory && SUB_CATEGORY_TEMPLATES[selectedSubCategory]
                ? `Professional requirements for ${selectedSubCategory} have been applied.`
                : "Select itemized requirements or add custom ones. Precision improves matching."}
            </p>

            <div className="requirements-grid">
              {(() => {
                const activeTemplate = selectedSubCategory && SUB_CATEGORY_TEMPLATES[selectedSubCategory];
                const categoryDefault = selectedCategory && CATEGORY_DEFAULTS[selectedCategory];
                const dataSource = activeTemplate || categoryDefault || CATEGORY_DEFAULTS.Default;

                if (!dataSource || !dataSource.checklists) return null;

                const standardGroups = [
                  { id: 'core', label: 'Core Responsibilities' },
                  { id: 'technical', label: 'Technical Skills' },
                  { id: 'tools', label: 'Tools & Software' },
                  { id: 'soft', label: 'Soft Skills' },
                  { id: 'experience', label: 'Experience Requirements' },
                  { id: 'education', label: 'Education & Certifications' }
                ];

                return (
                  <>
                    {standardGroups.map(group => renderRequirementGroup(group.id, group.label, dataSource.checklists[group.id] || []))}
                    {dynamicCategories.map(group => renderRequirementGroup(group.id, group.label, [], true))}
                  </>
                );
              })()}

              <div className="add-category-control">
                {showAddCategory ? (
                  <div className="add-category-form">
                    <input
                      type="text"
                      value={newCategoryName}
                      onChange={(e) => setNewCategoryName(e.target.value)}
                      placeholder="Category Name (e.g. Benefits)"
                      autoFocus
                      onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCategory())}
                    />
                    <div className="add-actions">
                      <button type="button" className="btn-confirm" onClick={handleAddCategory}>Add</button>
                      <button type="button" className="btn-cancel" onClick={() => setShowAddCategory(false)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    className="btn-add-section"
                    onClick={() => setShowAddCategory(true)}
                  >
                    <Plus size={20} />
                    <span>Add Additional Category</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="form-footer">
            <button type="button" className="btn-clear" onClick={() => window.location.reload()}>
              Reset Draft
            </button>
            <button type="submit" className="btn-post" disabled={createJobMutation.isLoading}>
              {createJobMutation.isLoading ? 'Publishing...' : '🚀 Publish Job Posting'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

export default JobPosting
