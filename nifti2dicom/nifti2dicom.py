import argparse
import pydicom
import nibabel as nib
from nibabel import processing
import numpy as np
import os

def nifti2dicom(path_in, path_out, draft_path='template.dcm', modality='CT', y_flip=True, z_flip=True, x_flip=True, resample=False):
    ''' 
    Converts nifti images to dicom images.

    path_in: path to nifti data
    path_out: path to output dicom directory
    draft_path: path to draft dicom file
    y_flip: flip image in y direction
    z_flip: flip image in z direction
    '''

    os.makedirs(path_out, exist_ok=True)
    dcm_draft = pydicom.dcmread(draft_path)
    if modality == 'PET':
        dcm_draft.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.128'
    nii = nib.load(path_in)

    if resample:
        height = (nii.header['dim'][3]-1)*nii.header['pixdim'][3]
        z_spacing = height/200
        x_spacing = nii.header['pixdim'][1]
        y_spacing = nii.header['pixdim'][2]
        nii = processing.conform(nii, out_shape=[512, 512, 200], voxel_size=(x_spacing, y_spacing, z_spacing))

    # process nifti images
    imgs = nii.get_fdata().astype(np.int16)
    imgs = np.moveaxis(imgs, -1, 0)
    imgs = np.moveaxis(imgs, -1, 1)
    if x_flip:
        imgs = np.flip(imgs, axis=2)
    if y_flip:
        imgs = np.flip(imgs, axis=1)
    if z_flip:
        imgs = np.flip(imgs, axis=0)

    scale, intercept = [*nii.header.get_slope_inter()]
    if scale == None:
        scale = 1
    if intercept == None:
        intercept = 0
    
    # set general dicom tags
    dcm_draft.RescaleIntercept = intercept
    dcm_draft.RescaleSlope = scale
    slice_thickness = nii.header['pixdim'][3]
    x_dim, y_dim = nii.header['pixdim'][1], nii.header['pixdim'][2]
    dcm_draft.BitsStored = nii.header['bitpix']
    dcm_draft.PixelSpacing = [x_dim, y_dim]
    dcm_draft.SliceThickness = slice_thickness
    dcm_draft.SamplesPerPixel = 1
    dcm_draft.BitsAllocated = 16
    dcm_draft.BitsStored = 16
    dcm_draft.HighBit = 15
    dcm_draft.PixelRepresentation = 1
    dcm_draft.PhotometricInterpretation = 'MONOCHROME2'
    dcm_draft.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    dcm_draft.SOPClassUID = '1.2.840.10008.1.2'
    dcm_draft.Rows = imgs.shape[1]
    dcm_draft.Columns = imgs.shape[2]
    dcm_draft.Modality = modality

    for i, img in enumerate(imgs):
        dcm_draft.PixelData = img.astype(np.int16).tobytes()
        dcm_draft.InstanceNumber = i+1
        pydicom.write_file(path_out + '/' + str(i+1) + '.dcm', dcm_draft)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='nifti2dicom', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('src')
    parser.add_argument('dest') 
    parser.add_argument('-d', '--draft', action='store', default='template.dcm')
    parser.add_argument('-m', '--modality', action='store', default='template.dcm')
    parser.add_argument('-x', '--x_flip', action='store_false')
    parser.add_argument('-y', '--y_flip', action='store_false')
    parser.add_argument('-z', '--z_flip', action='store_false')

    args = vars(parser.parse_args())
    
    nifti2dicom(path_in=args['src'], path_out=args['dest'], draft_path=args['draft'], modality=args['modality'], x_flip=args['x_flip'], y_flip=args['y_flip'], z_flip=args['z_flip'])
