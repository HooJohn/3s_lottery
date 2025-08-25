import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Camera, 
  Upload, 
  Check, 
  AlertCircle, 
  ArrowLeft, 
  ArrowRight,
  User,
  CreditCard,
  Car,
  Vote
} from 'lucide-react';
import toast from 'react-hot-toast';

import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import Layout from '../../components/layout/Layout';
import { cn } from '../../utils/cn';

// KYC步骤枚举
enum KYCStep {
  INTRO = 'intro',
  DOCUMENT_TYPE = 'document_type',
  UPLOAD_FRONT = 'upload_front',
  UPLOAD_BACK = 'upload_back',
  SELFIE = 'selfie',
  REVIEW = 'review',
  SUBMITTED = 'submitted',
}

// 证件类型
const documentTypes = [
  {
    key: 'NIN',
    label: '国民身份证号',
    description: '尼日利亚国民身份证',
    icon: User,
    requiresBack: false,
  },
  {
    key: 'PASSPORT',
    label: '国际护照',
    description: '有效的国际护照',
    icon: CreditCard,
    requiresBack: false,
  },
  {
    key: 'DRIVERS_LICENSE',
    label: '驾驶证',
    description: '有效的驾驶执照',
    icon: Car,
    requiresBack: true,
  },
  {
    key: 'VOTERS_CARD',
    label: '选民卡',
    description: '永久选民卡',
    icon: Vote,
    requiresBack: true,
  },
];

interface UploadedFile {
  file: File;
  preview: string;
}

const KYCPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<KYCStep>(KYCStep.INTRO);
  const [selectedDocumentType, setSelectedDocumentType] = useState<string>('');
  const [documentNumber, setDocumentNumber] = useState('');
  const [frontImage, setFrontImage] = useState<UploadedFile | null>(null);
  const [backImage, setBackImage] = useState<UploadedFile | null>(null);
  const [selfieImage, setSelfieImage] = useState<UploadedFile | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const frontInputRef = useRef<HTMLInputElement>(null);
  const backInputRef = useRef<HTMLInputElement>(null);
  const selfieInputRef = useRef<HTMLInputElement>(null);

  const selectedDocument = documentTypes.find(doc => doc.key === selectedDocumentType);

  // 处理文件上传
  const handleFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>,
    type: 'front' | 'back' | 'selfie'
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      toast.error('请上传图片文件');
      return;
    }

    // 验证文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('文件大小不能超过5MB');
      return;
    }

    const preview = URL.createObjectURL(file);
    const uploadedFile = { file, preview };

    switch (type) {
      case 'front':
        setFrontImage(uploadedFile);
        break;
      case 'back':
        setBackImage(uploadedFile);
        break;
      case 'selfie':
        setSelfieImage(uploadedFile);
        break;
    }
  };

  // 提交KYC申请
  const submitKYC = async () => {
    if (!frontImage || !selfieImage) {
      toast.error('请上传所有必需的文件');
      return;
    }

    if (selectedDocument?.requiresBack && !backImage) {
      toast.error('请上传证件背面');
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('document_type', selectedDocumentType);
      formData.append('document_number', documentNumber);
      formData.append('front_image', frontImage.file);
      if (backImage) {
        formData.append('back_image', backImage.file);
      }
      formData.append('selfie_image', selfieImage.file);

      const response = await fetch('/api/v1/auth/kyc/submit/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setCurrentStep(KYCStep.SUBMITTED);
        toast.success('KYC申请提交成功！');
      } else {
        toast.error(result.message || 'KYC申请提交失败');
      }
    } catch (error) {
      console.error('KYC submission error:', error);
      toast.error('网络错误，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 渲染步骤指示器
  const renderStepIndicator = () => {
    const steps = [
      { key: KYCStep.INTRO, label: '介绍', number: 1 },
      { key: KYCStep.DOCUMENT_TYPE, label: '选择证件', number: 2 },
      { key: KYCStep.UPLOAD_FRONT, label: '上传正面', number: 3 },
      { key: KYCStep.UPLOAD_BACK, label: '上传背面', number: 4 },
      { key: KYCStep.SELFIE, label: '自拍验证', number: 5 },
      { key: KYCStep.REVIEW, label: '审核提交', number: 6 },
    ];

    const currentStepIndex = steps.findIndex(step => step.key === currentStep);

    return (
      <div className="flex items-center justify-center mb-8 overflow-x-auto">
        {steps.map((step, index) => {
          const isActive = currentStep === step.key;
          const isCompleted = index < currentStepIndex;
          const isSkipped = step.key === KYCStep.UPLOAD_BACK && !selectedDocument?.requiresBack;
          
          if (isSkipped) return null;

          return (
            <React.Fragment key={step.key}>
              <div className="flex flex-col items-center min-w-0">
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-2 transition-colors',
                    isActive
                      ? 'bg-primary-500 text-white'
                      : isCompleted
                      ? 'bg-success-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  )}
                >
                  {isCompleted ? <Check className="w-4 h-4" /> : step.number}
                </div>
                <span
                  className={cn(
                    'text-xs font-medium text-center',
                    isActive ? 'text-primary-600' : 'text-gray-500'
                  )}
                >
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && !isSkipped && (
                <div
                  className={cn(
                    'w-8 h-0.5 mx-2 mt-4 transition-colors',
                    isCompleted ? 'bg-success-500' : 'bg-gray-200'
                  )}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  // 渲染介绍页面
  const renderIntroStep = () => (
    <div className="text-center space-y-6">
      <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto">
        <FileText className="w-10 h-10 text-primary-600" />
      </div>
      
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">身份验证</h2>
        <p className="text-gray-600 mb-6">
          为了确保您的账户安全并遵守法规要求，我们需要验证您的身份。
          这个过程通常在24-48小时内完成。
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">您需要准备：</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• 有效的身份证件（正反面清晰照片）</li>
          <li>• 手持证件的自拍照</li>
          <li>• 确保照片清晰，所有信息可见</li>
          <li>• 文件大小不超过5MB</li>
        </ul>
      </div>

      <Button
        onClick={() => setCurrentStep(KYCStep.DOCUMENT_TYPE)}
        variant="primary"
        size="lg"
        fullWidth
      >
        开始验证
      </Button>
    </div>
  );

  // 渲染证件类型选择
  const renderDocumentTypeStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">选择证件类型</h2>
        <p className="text-gray-600">请选择您要上传的身份证件类型</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {documentTypes.map((docType) => {
          const Icon = docType.icon;
          return (
            <button
              key={docType.key}
              onClick={() => setSelectedDocumentType(docType.key)}
              className={cn(
                'p-6 border-2 rounded-lg transition-all duration-200 text-left',
                selectedDocumentType === docType.key
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <div className="flex items-start space-x-4">
                <div className={cn(
                  'w-12 h-12 rounded-lg flex items-center justify-center',
                  selectedDocumentType === docType.key
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-600'
                )}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {docType.label}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {docType.description}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {selectedDocumentType && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            证件号码
          </label>
          <input
            type="text"
            value={documentNumber}
            onChange={(e) => setDocumentNumber(e.target.value)}
            placeholder="请输入证件号码"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      )}

      <div className="flex space-x-4">
        <Button
          onClick={() => setCurrentStep(KYCStep.INTRO)}
          variant="outline"
          className="flex-1"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          上一步
        </Button>
        <Button
          onClick={() => setCurrentStep(KYCStep.UPLOAD_FRONT)}
          variant="primary"
          className="flex-1"
          disabled={!selectedDocumentType || !documentNumber}
        >
          下一步
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );

  // 渲染文件上传组件
  const renderFileUpload = (
    type: 'front' | 'back' | 'selfie',
    title: string,
    description: string,
    uploadedFile: UploadedFile | null,
    inputRef: React.RefObject<HTMLInputElement>
  ) => (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600">{description}</p>
      </div>

      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
          uploadedFile
            ? 'border-success-300 bg-success-50'
            : 'border-gray-300 hover:border-gray-400'
        )}
        onClick={() => inputRef.current?.click()}
      >
        {uploadedFile ? (
          <div className="space-y-4">
            <img
              src={uploadedFile.preview}
              alt="上传的文件"
              className="max-w-full max-h-64 mx-auto rounded-lg"
            />
            <div className="flex items-center justify-center text-success-600">
              <Check className="w-5 h-5 mr-2" />
              文件上传成功
            </div>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                inputRef.current?.click();
              }}
              variant="outline"
              size="sm"
            >
              重新上传
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
              {type === 'selfie' ? (
                <Camera className="w-8 h-8 text-gray-400" />
              ) : (
                <Upload className="w-8 h-8 text-gray-400" />
              )}
            </div>
            <div>
              <p className="text-gray-600 mb-2">
                点击上传或拖拽文件到此处
              </p>
              <p className="text-sm text-gray-500">
                支持 JPG、PNG 格式，最大 5MB
              </p>
            </div>
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={(e) => handleFileUpload(e, type)}
        className="hidden"
      />

      {/* 要求提示 */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div className="text-sm text-yellow-800">
            <p className="font-semibold mb-1">拍照要求：</p>
            <ul className="space-y-1">
              <li>• 图像清晰，所有文字可读</li>
              <li>• 证件四个角落完整可见</li>
              <li>• 避免反光和阴影</li>
              {type === 'selfie' && <li>• 手持证件，面部和证件都清晰可见</li>}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  // 渲染审核页面
  const renderReviewStep = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">审核信息</h2>
        <p className="text-gray-600">请确认您上传的信息无误</p>
      </div>

      <div className="space-y-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">证件信息</h3>
          <p className="text-gray-600">
            类型：{selectedDocument?.label}
          </p>
          <p className="text-gray-600">
            号码：{documentNumber}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {frontImage && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">证件正面</h4>
              <img
                src={frontImage.preview}
                alt="证件正面"
                className="w-full h-32 object-cover rounded-lg border"
              />
            </div>
          )}
          
          {backImage && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">证件背面</h4>
              <img
                src={backImage.preview}
                alt="证件背面"
                className="w-full h-32 object-cover rounded-lg border"
              />
            </div>
          )}
          
          {selfieImage && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">手持证件自拍</h4>
              <img
                src={selfieImage.preview}
                alt="手持证件自拍"
                className="w-full h-32 object-cover rounded-lg border"
              />
            </div>
          )}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">提交后：</p>
            <ul className="space-y-1">
              <li>• 我们将在24-48小时内审核您的文件</li>
              <li>• 审核结果将通过短信和邮件通知您</li>
              <li>• 如有问题，我们会联系您补充材料</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="flex space-x-4">
        <Button
          onClick={() => setCurrentStep(KYCStep.SELFIE)}
          variant="outline"
          className="flex-1"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          上一步
        </Button>
        <Button
          onClick={submitKYC}
          variant="primary"
          className="flex-1"
          loading={isSubmitting}
          disabled={isSubmitting}
        >
          提交审核
        </Button>
      </div>
    </div>
  );

  // 渲染提交成功页面
  const renderSubmittedStep = () => (
    <div className="text-center space-y-6">
      <div className="w-20 h-20 bg-success-100 rounded-full flex items-center justify-center mx-auto">
        <Check className="w-10 h-10 text-success-600" />
      </div>
      
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">提交成功！</h2>
        <p className="text-gray-600 mb-6">
          您的身份验证申请已成功提交。我们将在24-48小时内完成审核，
          审核结果将通过短信和邮件通知您。
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="font-semibold text-green-900 mb-2">接下来：</h3>
        <ul className="text-sm text-green-800 space-y-1">
          <li>• 请保持手机畅通，我们可能会联系您</li>
          <li>• 您可以在个人中心查看审核状态</li>
          <li>• 审核通过后即可享受完整服务</li>
        </ul>
      </div>

      <Button
        onClick={() => navigate('/profile')}
        variant="primary"
        size="lg"
        fullWidth
      >
        查看审核状态
      </Button>
    </div>
  );

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="p-8">
            {renderStepIndicator()}
            
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {currentStep === KYCStep.INTRO && renderIntroStep()}
                {currentStep === KYCStep.DOCUMENT_TYPE && renderDocumentTypeStep()}
                {currentStep === KYCStep.UPLOAD_FRONT && renderFileUpload(
                  'front',
                  '上传证件正面',
                  '请上传您证件的正面照片',
                  frontImage,
                  frontInputRef
                )}
                {currentStep === KYCStep.UPLOAD_BACK && renderFileUpload(
                  'back',
                  '上传证件背面',
                  '请上传您证件的背面照片',
                  backImage,
                  backInputRef
                )}
                {currentStep === KYCStep.SELFIE && renderFileUpload(
                  'selfie',
                  '手持证件自拍',
                  '请手持证件拍摄一张自拍照',
                  selfieImage,
                  selfieInputRef
                )}
                {currentStep === KYCStep.REVIEW && renderReviewStep()}
                {currentStep === KYCStep.SUBMITTED && renderSubmittedStep()}
              </motion.div>
            </AnimatePresence>

            {/* 导航按钮 */}
            {currentStep !== KYCStep.INTRO && 
             currentStep !== KYCStep.DOCUMENT_TYPE && 
             currentStep !== KYCStep.REVIEW && 
             currentStep !== KYCStep.SUBMITTED && (
              <div className="flex space-x-4 mt-8">
                <Button
                  onClick={() => {
                    const steps = [KYCStep.UPLOAD_FRONT, KYCStep.UPLOAD_BACK, KYCStep.SELFIE];
                    const currentIndex = steps.indexOf(currentStep);
                    if (currentIndex > 0) {
                      const prevStep = steps[currentIndex - 1];
                      if (prevStep === KYCStep.UPLOAD_BACK && !selectedDocument?.requiresBack) {
                        setCurrentStep(KYCStep.UPLOAD_FRONT);
                      } else {
                        setCurrentStep(prevStep);
                      }
                    } else {
                      setCurrentStep(KYCStep.DOCUMENT_TYPE);
                    }
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  上一步
                </Button>
                <Button
                  onClick={() => {
                    const steps = [KYCStep.UPLOAD_FRONT, KYCStep.UPLOAD_BACK, KYCStep.SELFIE];
                    const currentIndex = steps.indexOf(currentStep);
                    if (currentIndex < steps.length - 1) {
                      const nextStep = steps[currentIndex + 1];
                      if (nextStep === KYCStep.UPLOAD_BACK && !selectedDocument?.requiresBack) {
                        setCurrentStep(KYCStep.SELFIE);
                      } else {
                        setCurrentStep(nextStep);
                      }
                    } else {
                      setCurrentStep(KYCStep.REVIEW);
                    }
                  }}
                  variant="primary"
                  className="flex-1"
                  disabled={
                    (currentStep === KYCStep.UPLOAD_FRONT && !frontImage) ||
                    (currentStep === KYCStep.UPLOAD_BACK && !backImage) ||
                    (currentStep === KYCStep.SELFIE && !selfieImage)
                  }
                >
                  下一步
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default KYCPage;